using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Threading;
using System.Diagnostics;

namespace UploadBlobs
{
	internal class Constants
	{
		public static long BytesPerGB = 1024 * 1024 * 1024;
		public static long MaxBlobSizeInBytes = 400 * BytesPerGB;
	}

	internal class ImageFile
	{
		public string Path { get; set; }
		public long SizeInBytes { get; set; }
	};

	internal class Blob
	{
		public static string ManifestSuffix = "-manifest.txt";

		public string Name { get; set; }
		public List<ImageFile> ImageFiles { get; private set; }
		public long SizeInBytes { get; set; }
		public long MaxSizeInBytes { get; private set; }

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
		}

		public string GetManifestFilePath(string dir)
		{
			return Path.Combine(dir, String.Format("{0}{1}", Name, ManifestSuffix));
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

		public void Upload(string tempDir, Action<double, double> onComplete, Func<bool> shouldStop)
		{
			if (shouldStop())
				return;

			var createStopwatch = new Stopwatch();
			var uploadStopwatch = new Stopwatch();

			try
			{
				createStopwatch.Start();
				var archiveFilePath = CreateArchive(tempDir);
				createStopwatch.Stop();

				if (shouldStop())
					return;

				uploadStopwatch.Start();
				UploadArchive(archiveFilePath);
				uploadStopwatch.Stop();

				File.Delete(archiveFilePath);
			}
			catch (Exception e)
			{
				Console.WriteLine("Error uploading {0}: {1}", Name, e);
			}

			onComplete(
				SizeInBytes / (createStopwatch.ElapsedMilliseconds / 1000.0),
				SizeInBytes / (uploadStopwatch.ElapsedMilliseconds / 1000.0));
		}

		private string CreateArchive(string tempDir)
		{
			var archiveFilePath = Path.Combine(tempDir, Name) + ".zip";
			Console.WriteLine("Creating archive: {0}", archiveFilePath);
			File.WriteAllText(archiveFilePath, "dummy");
			Thread.Sleep(4000);
			// TODO
			return archiveFilePath;
		}
		
		private void UploadArchive(string archiveFilePath)
		{
			Console.WriteLine("Uploading archive: {0}", archiveFilePath);
			Thread.Sleep(6000);
			// TODO
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
				// Temp
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
		private long _tempDirQuotaInBytes;
		private string _azureToken;
		private string _completedBlobsFilePath;
		private string _stopSentinelFilePath;

		private List<Blob> _completedBlobs = new List<Blob>();
		private List<Blob> _uploadingBlobs = new List<Blob>();
		private Queue<Blob> _pendingBlobs = new Queue<Blob>();
		double _lastCreateBytesPerSecond = 0;
		double _lastUploadBytesPerSecond = 0;
		private Mutex _mutex = new Mutex();

		public RunCommand(string tempDir, long tempDirQuotaInBytes, string azureToken)
		{
			_tempDir = tempDir;
			_tempDirQuotaInBytes = tempDirQuotaInBytes;
			_azureToken = azureToken;

			_completedBlobsFilePath = Path.Combine(_tempDir, "completed.txt");
			_stopSentinelFilePath = Path.Combine(_tempDir, "stop.txt");
		}

		public void Execute()
		{
			LoadBlobs();
			UploadBlobs();
		}

		private void LoadBlobs()
		{
			var completedBlobNames = new HashSet<string>();
			if (File.Exists(_completedBlobsFilePath))
			{
				var lines = File.ReadLines(_completedBlobsFilePath);
				foreach (var line in lines)
				{
					completedBlobNames.Add(line);
				}
			}

			foreach (var blobManifestFilePath in Directory.EnumerateFiles(_tempDir, "*" + Blob.ManifestSuffix))
			{
				var blobManifestFileName = Path.GetFileName(blobManifestFilePath);
				var blobName = blobManifestFileName.Substring(0, blobManifestFileName.IndexOf(Blob.ManifestSuffix));
				var blob = new Blob(blobName, long.MaxValue);
				blob.AddImageFilesFromManifest(blobManifestFilePath);
				if (completedBlobNames.Contains(blobName))
					_completedBlobs.Add(blob);
				else
					_pendingBlobs.Enqueue(blob);
			}
		}

		private void UploadBlobs()
		{
			while (true)
			{
				lock (_mutex)
				{
					if (_pendingBlobs.Count == 0 || ShouldStop())
						return;

					while (TempDirQuotaBytesUsed() + _pendingBlobs.Peek().SizeInBytes < _tempDirQuotaInBytes)
					{
						var blob = _pendingBlobs.Dequeue();
						_uploadingBlobs.Add(blob);
						var thread = new Thread(() =>
						{
							blob.Upload(
								_tempDir,
								(createBytesPerSecond, uploadBytesPerSecond) => { CompleteBlob(blob, createBytesPerSecond, uploadBytesPerSecond); },
								ShouldStop);
						});
						thread.Start();
					}

					Console.WriteLine("\r{0} blob(s) completed, {1} blob(s) uploading, {2} blob(s) pending ({3:0}Mbps creation, {4:0}Mbps upload)     ",
						_completedBlobs.Count,
						_uploadingBlobs.Count,
						_pendingBlobs.Count,
						_lastCreateBytesPerSecond / (1000.0 * 1000.0),
						_lastUploadBytesPerSecond / (1000.0 * 1000.0));
				}

				Thread.Sleep(500);
			}
		}

		private long TempDirQuotaBytesUsed()
		{
			long bytes = 0;
			_uploadingBlobs.ForEach(x => bytes += x.SizeInBytes);
			return bytes;
		}

		private void CompleteBlob(Blob blob, double createBytesPerSecond, double uploadBytesPerSecond)
		{
			lock (_mutex)
			{
				_completedBlobs.Add(blob);
				_uploadingBlobs.Remove(blob);
				_lastCreateBytesPerSecond = createBytesPerSecond;
				_lastUploadBytesPerSecond = uploadBytesPerSecond;

				using (var writer = File.AppendText(_completedBlobsFilePath))
				{
					writer.WriteLine(blob.Name);
				}
			}
		}

		private bool ShouldStop()
		{
			lock (_mutex)
			{
				if (File.Exists(_stopSentinelFilePath))
				{
					Console.WriteLine("Stop signal received");
					File.Delete(_stopSentinelFilePath);
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
				Console.WriteLine("UploadBlobs run <temp quota in GB> <Azure SAS URL token>");
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
				var command = new RunCommand(Directory.GetCurrentDirectory(), Constants.BytesPerGB * int.Parse(args[1]), args[2]);
				command.Execute();
			}
		}
	}
}
