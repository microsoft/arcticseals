using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Threading;
using System.Diagnostics;
using Microsoft.WindowsAzure.Storage;
using Microsoft.WindowsAzure.Storage.Blob;
using Microsoft.WindowsAzure.Storage.Auth;

namespace UploadBlobs
{
	internal class Constants
	{
		public static long BytesPerGB = 1024 * 1024 * 1024;
		public static long MaxBlobSizeInBytes = 1 * BytesPerGB;
	}

	internal class ImageFile
	{
		public string Path { get; set; }
		public long SizeInBytes { get; set; }
	};

	internal class Blob
	{
		private Dictionary<string, int> _imageFileCountByDrive = new Dictionary<string, int>();

		public static string ManifestSuffix = "-manifest.txt";

		public string Name { get; set; }
		public List<ImageFile> ImageFiles { get; private set; }
		public long SizeInBytes { get; set; }
		public long MaxSizeInBytes { get; private set; }
		public string PrimarySourceDrive
		{
			get
			{
				string result = "";
				int resultCount = 0;
				foreach (var kvp in _imageFileCountByDrive)
				{
					if (kvp.Value > resultCount)
					{
						result = kvp.Key;
						resultCount = kvp.Value;
					}
				}
				return result;
			}
		}

		public Blob(string name, long maxSizeInBytes)
		{
			Name = name;
			ImageFiles = new List<ImageFile>();
			SizeInBytes = 0;
			MaxSizeInBytes = maxSizeInBytes;
		}

		public bool CanAddImageFile(ImageFile imageFile)
		{
			return SizeInBytes + imageFile.SizeInBytes <= MaxSizeInBytes;
		}

		public void AddImageFile(ImageFile imageFile)
		{
			if (!CanAddImageFile(imageFile))
			{
				throw new ArgumentException();
			}

			ImageFiles.Add(imageFile);
			SizeInBytes += imageFile.SizeInBytes;

			var drive = imageFile.Path.Substring(0, 2);
			if (!_imageFileCountByDrive.ContainsKey(drive))
			{
				_imageFileCountByDrive[drive] = 0;
			}
			else
			{
				_imageFileCountByDrive[drive] = _imageFileCountByDrive[drive] + 1;
			}
		}

		public string GetManifestFilePath(string dir)
		{
			return Path.Combine(dir, String.Format("{0}{1}", Name, ManifestSuffix));
		}

		public string GetArchiveFilePath(string dir)
		{
			return Path.Combine(dir, Name) + ".zip";
		}

		public void AddImageFilesFromManifest(string manifestFilePath)
		{
			foreach (var line in File.ReadLines(manifestFilePath))
			{
				var split = line.Split(';');
				var imageFile = new ImageFile();
				imageFile.Path = split[0];
				imageFile.SizeInBytes = long.Parse(split[1]);
				AddImageFile(imageFile);
			}
		}

		public void WriteManifest(string manifestFilePath)
		{
			using (var writer = File.CreateText(manifestFilePath))
			{
				foreach (var imageFile in ImageFiles)
				{
					writer.WriteLine("{0};{1}", imageFile.Path, imageFile.SizeInBytes);
				}
			}
		}

		public void Archive(string tempDir, Action onComplete, Func<bool> shouldStop)
		{
			var archiveFilePath = GetArchiveFilePath(tempDir);
			Program.Log("Archiving {0} ({1} files, {2:0.0}GB, primary drive {3})", Name, ImageFiles.Count, SizeInBytes / ((double)Constants.BytesPerGB), PrimarySourceDrive);

			try
			{
				using (var zipFileStream = new FileStream(archiveFilePath, FileMode.Create))
				{
					using (var zipArchive = new ZipArchive(zipFileStream, ZipArchiveMode.Create))
					{
						foreach (var imageFile in ImageFiles)
						{
							zipArchive.CreateEntryFromFile(imageFile.Path, Path.GetFileName(imageFile.Path), CompressionLevel.NoCompression);
							break; //TEMP
						}
					}
				}
			}
			catch (Exception e)
			{
				Program.Log("ERROR archiving {0}: {1}", Name, e);
			}

			onComplete();
		}

		public void Upload(string tempDir, string azureToken, Action onComplete, Func<bool> shouldStop)
		{
			// The Azure blob API allocates memory for the entire blob being uploaded, so skip this for now... upload has to be done manually.
			// See https://stackoverflow.com/questions/53963069/how-to-avoid-c-sharp-azure-api-from-running-out-of-memory-for-large-blob-uploads
			onComplete();
			return;

			Program.Log("Uploading {0}", Name);

			try
			{
				var container = new CloudBlobContainer(new Uri(azureToken));

				var archiveFilePath = GetArchiveFilePath(tempDir);
				var blob = container.GetBlockBlobReference(Path.GetFileName(archiveFilePath) + "-test");
				const int bufferSize = 64 * 1024 * 1024; // 64MB
				blob.StreamWriteSizeInBytes = bufferSize;
				using (var writeStream = blob.OpenWrite())
				{
					using (var readStream = new FileStream(archiveFilePath, FileMode.Open))
					{
						var buffer = new byte[bufferSize];
						var bytesRead = 0;
						while ((bytesRead = readStream.Read(buffer, 0, bufferSize)) != 0)
						{
							writeStream.Write(buffer, 0, bytesRead);
						}
					}
				}

				File.Delete(archiveFilePath);
			}
			catch (Exception e)
			{
				Program.Log("Error uploading {0}: {1}", Name, e);
			}

			onComplete();
		}
	}

	internal class BlobGroup
	{
		private List<ImageFile> _queuedImageFiles = new List<ImageFile>();

		public string Name { get; private set; }
		public List<Blob> Blobs { get; private set; }

		public BlobGroup(string name)
		{
			Name = name;
			Blobs = new List<Blob>();
		}

		public void AddImageFile(ImageFile imageFile)
		{
			_queuedImageFiles.Add(imageFile);
		}

		public void FinalizeBlobs()
		{
			_queuedImageFiles.Sort((a, b) => a.Path.CompareTo(b.Path));
			_queuedImageFiles.ForEach(imageFile =>
			{
				bool needNewBlob = Blobs.Count == 0 || !Blobs.Last().CanAddImageFile(imageFile);

				if (needNewBlob)
				{
					var blobName = String.Format("{0}_{1:00}", Name, Blobs.Count());
					Blobs.Add(new Blob(blobName, Blobs.Count == 0 ? Constants.MaxBlobSizeInBytes / 10 : Constants.MaxBlobSizeInBytes)); // First blob is 10% the size of the rest
				}

				Blobs.Last().AddImageFile(imageFile);
			});
		}

		public void WriteManifests(string tempDir)
		{
			foreach (var blob in Blobs)
			{
				blob.WriteManifest(blob.GetManifestFilePath(tempDir));
			}
		}
	}

	internal class PrepCommand
	{
		private string _tempDir;
		private string[] _sourceDirs;
		private Dictionary<string, BlobGroup> _blobGroupsByName = new Dictionary<string, BlobGroup>();
		private List<string> _skippedImageFiles = new List<string>();
		private int _totalImageFilesAdded = 0;

		public PrepCommand(string tempDir, string[] sourceDirs)
		{
			_tempDir = tempDir;
			_sourceDirs = sourceDirs;
		}

		public void Execute()
		{
			foreach (var sourceDir in _sourceDirs)
			{
				AddImageFilesInSourceDir(sourceDir);
			}

			foreach (var blobGroup in _blobGroupsByName.Values)
			{
				blobGroup.FinalizeBlobs();
				blobGroup.WriteManifests(_tempDir);
			}

			PrintPlan();
		}

		private void AddImageFilesInSourceDir(string path)
		{
			foreach (var blobGroupDir in Directory.GetDirectories(path).Where(x => { return !x.Contains("System Volume Information") && !x.Contains("$RECYCLE"); }))
			{
				AddImageFilesInBlobGroupDir(blobGroupDir);
			}
		}

		private void AddImageFilesInBlobGroupDir(string blobGroupDir)
		{
			var blobGroupName = Path.GetFileName(blobGroupDir);

			// Some directories have names that should all resolve to this base name if it is contained as a substring
			const string SpecialCaseHackBlobGroup = "TrainingBackground_ColorImages";
			if (blobGroupName.Contains(SpecialCaseHackBlobGroup))
			{
				blobGroupName = SpecialCaseHackBlobGroup;
			}

			if (!_blobGroupsByName.ContainsKey(blobGroupName))
			{
				_blobGroupsByName.Add(blobGroupName, new BlobGroup(blobGroupName));
			}
			var blobGroup = _blobGroupsByName[blobGroupName];

			AddImageFilesToBlobGroup(Directory.GetFiles(blobGroupDir), blobGroup);
		}

		private void AddImageFilesToBlobGroup(string[] filePaths, BlobGroup blobGroup)
		{
			foreach (var filePath in filePaths)
			{
				// Uncomment for testing
				//if (_totalImageFilesAdded > 50000)
					//return;

				var extension = Path.GetExtension(filePath).ToLowerInvariant();
				if (extension == ".png" || extension == ".jpg")
				{
					var imageFile = new ImageFile();
					imageFile.Path = filePath;
					imageFile.SizeInBytes = new FileInfo(filePath).Length;
					blobGroup.AddImageFile(imageFile);

					if (++_totalImageFilesAdded % 1000 == 0)
					{
						Console.Write("\r{0} files added, {1} files skipped", _totalImageFilesAdded, _skippedImageFiles.Count);
					}
				}
				else
				{
					_skippedImageFiles.Add(filePath);
				}
			}
		}

		private void PrintPlan()
		{
			Console.WriteLine("");
			foreach (var blobGroup in _blobGroupsByName.Values)
			{
				Console.WriteLine("{0} ({1} blobs to upload)", blobGroup.Name, blobGroup.Blobs.Count);
			}
			Console.WriteLine("{0} skipped files", _skippedImageFiles.Count);
		}
	}

	internal class RunCommand
	{
		private string _tempDir;
		private string _azureToken;
		private string _uploadedBlobsFilePath;
		private string _stopSentinelFilePath;

		private long _totalBytesToUpload = 0;
		private List<Blob> _pendingBlobs = new List<Blob>();
		private List<Blob> _archivingBlobs = new List<Blob>();
		private List<Blob> _archivedBlobs = new List<Blob>();
		private List<Blob> _uploadingBlobs = new List<Blob>();
		private List<Blob> _uploadedBlobs = new List<Blob>();
		private Stopwatch _stopwatch = new Stopwatch();
		private Mutex _mutex = new Mutex();

		public RunCommand(string tempDir, string azureToken)
		{
			_tempDir = tempDir;
			_azureToken = azureToken;

			_uploadedBlobsFilePath = Path.Combine(_tempDir, "uploaded.txt");
			_stopSentinelFilePath = Path.Combine(_tempDir, "stop.txt");
		}

		public void Execute()
		{
			LoadBlobs();
			ProcessBlobs();
		}

		private void LoadBlobs()
		{
			var uploadedBlobNames = new HashSet<string>();
			if (File.Exists(_uploadedBlobsFilePath))
			{
				var lines = File.ReadLines(_uploadedBlobsFilePath);
				foreach (var line in lines)
				{
					uploadedBlobNames.Add(line);
				}
			}

			int totalImageFiles = 0;
			foreach (var blobManifestFilePath in Directory.EnumerateFiles(_tempDir, "*" + Blob.ManifestSuffix))
			{
				var blobManifestFileName = Path.GetFileName(blobManifestFilePath);
				var blobName = blobManifestFileName.Substring(0, blobManifestFileName.IndexOf(Blob.ManifestSuffix));
				var blob = new Blob(blobName, long.MaxValue);
				blob.AddImageFilesFromManifest(blobManifestFilePath);
				if (!uploadedBlobNames.Contains(blobName))
				{
					_pendingBlobs.Add(blob);
					totalImageFiles += blob.ImageFiles.Count;
					_totalBytesToUpload += blob.SizeInBytes;
				}
			}

			Program.Log("Uploading {0} blobs ({1:0.0}GB) containing {2} files", _pendingBlobs.Count, _totalBytesToUpload / ((double)Constants.BytesPerGB), totalImageFiles);
		}

		private void ProcessBlobs()
		{
			_stopwatch.Start();

			while (true)
			{
				lock (_mutex)
				{
					if (_pendingBlobs.Count + _archivingBlobs.Count + _archivedBlobs.Count + _uploadingBlobs.Count == 0 || ShouldStop())
						return;

					// Look for pending blobs ready to archive
					if (_pendingBlobs.Count > 0)
					{
						var sourceDrivesInUse = new HashSet<string>();
						_archivingBlobs.ForEach(x => sourceDrivesInUse.Add(x.PrimarySourceDrive));

						var blob = _pendingBlobs.FirstOrDefault(x =>
							!sourceDrivesInUse.Contains(x.PrimarySourceDrive) &&
							SufficientTempDirSpaceForArchive(x.SizeInBytes));

						// If we couldn't find a pending blob using a different drive, look for any blob that fits in the remaining quota
						if (blob == null)
						{
							blob = _pendingBlobs.FirstOrDefault(x => SufficientTempDirSpaceForArchive(x.SizeInBytes));
						}

						if (blob != null)
						{
							_pendingBlobs.Remove(blob);
							_archivingBlobs.Add(blob);

							var thread = new Thread(() =>
							{
								blob.Archive(_tempDir, () => OnCompleteBlobArchive(blob), ShouldStop);
							});
							thread.Start();
						}
					}

					// Look for archived blobs ready to upload
					foreach (var blob in _archivedBlobs.ToArray())
					{
						_archivedBlobs.Remove(blob);
						_uploadingBlobs.Add(blob);

						var thread = new Thread(() =>
						{
							blob.Upload(_tempDir, _azureToken, () => OnCompleteBlobUpload(blob), ShouldStop);
						});
						thread.Start();
					}
				}

				Thread.Sleep(1000);
			}
		}

		private bool SufficientTempDirSpaceForArchive(long archiveSizeInBytes)
		{
			var tempDrive = _tempDir.Substring(0, 3).ToLowerInvariant();
			long tempDriveFreeSpaceInBytes = 0;
			foreach (DriveInfo drive in DriveInfo.GetDrives())
			{
				if (drive.IsReady && drive.Name.ToLowerInvariant() == tempDrive)
				{
					tempDriveFreeSpaceInBytes = drive.AvailableFreeSpace;
					break;
				}
			}

			return tempDriveFreeSpaceInBytes - archiveSizeInBytes > 100 * Constants.BytesPerGB; // Leave 100GB buffer
		}

		private long BytesUploaded()
		{
			long bytes = 0;
			_uploadedBlobs.ForEach(x => bytes += x.SizeInBytes);
			return bytes;
		}

		private void OnCompleteBlobArchive(Blob blob)
		{
			lock (_mutex)
			{
				_archivingBlobs.Remove(blob);
				_archivedBlobs.Add(blob);
			}
		}

		private void OnCompleteBlobUpload(Blob blob)
		{
			lock (_mutex)
			{
				_uploadingBlobs.Remove(blob);
				_uploadedBlobs.Add(blob);

				using (var writer = File.AppendText(_uploadedBlobsFilePath))
				{
					writer.WriteLine(blob.Name);
				}

				double fractionDone = BytesUploaded() / ((double)_totalBytesToUpload);

				Console.WriteLine("{3}: Completed {0} ({1:0.0}% done, {2:0.0} hours remaining)",
					blob.Name,
					100.0 * fractionDone,
					_stopwatch.Elapsed.TotalHours / fractionDone - _stopwatch.Elapsed.TotalHours,
					DateTime.Now);
			}
		}

		private bool ShouldStop()
		{
			lock (_mutex)
			{
				if (File.Exists(_stopSentinelFilePath))
				{
					return true;
				}
			}
			return false;
		}
	}

	class Program
	{
		static void Main(string[] args)
		{
			if(args.Length < 2)
			{
				Console.WriteLine("USAGE:");
				Console.WriteLine("");
				Console.WriteLine("UploadBlobs prep <comma-separated source dirs>");
				Console.WriteLine("UploadBlobs run <Azure SAS URL token>");
				Console.WriteLine("");
				Console.WriteLine("Temp files are stored in current directory.");
				return;
			}
			if (args[0].Equals("prep", StringComparison.OrdinalIgnoreCase))
			{
				var command = new PrepCommand(Directory.GetCurrentDirectory(), args[1].Split(','));
				command.Execute();
			}
			else if (args[0].Equals("run", StringComparison.OrdinalIgnoreCase))
			{
				var command = new RunCommand(Directory.GetCurrentDirectory(), args[1]);
				command.Execute();
			}
		}

		static public void Log(string format, params object[] args)
		{
			Console.WriteLine("{0}: {1}", DateTime.Now, String.Format(format, args));
		}
	}
}
