using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace CopyImageFiles
{
	public partial class Form1 : Form
	{
		const double BytesPerGB = 1024 * 1024 * 1024;

		private Dictionary<string, List<ImageFile>> _imagesByDateString = new Dictionary<string, List<ImageFile>>();
		private int _pathsExamined = 0;

		private List<ImageFile> _copyQueue = new List<ImageFile>();
		private int _imagesCopied = 0;
		private long _bytesCopied = 0;
		private List<ImageFile> _copyErrors = new List<ImageFile>();

		private enum ImageType
		{
			Unknown = 0,
			Thermal,
			Color
		};

		private class ImageFile
		{
			public string Path { get; set; }
			public ImageType Type { get; set; }
			public DateTime Timestamp { get; set; }
			public long SizeInBytes { get; set; }
		};

		public Form1()
		{
			InitializeComponent();
		}

		private DateTime ParseTimestamp(string s)
		{
			// Two possible formats, e.g.:
			// 160408_020848.724
			// 20160408235502.543GMT
			if (s.Length == 17)
			{
				try
				{
					var year = 2000 + int.Parse(s.Substring(0, 2));
					var month = int.Parse(s.Substring(2, 2));
					var day = int.Parse(s.Substring(4, 2));
					var hour = int.Parse(s.Substring(7, 2));
					var minute = int.Parse(s.Substring(9, 2));
					var second = int.Parse(s.Substring(11, 2));
					var millisecond = int.Parse(s.Substring(14, 3));
					return new DateTime(year, month, day, hour, minute, second, millisecond, DateTimeKind.Utc);
				}
				catch (Exception)
				{
					return DateTime.MaxValue;
				}
			}
			else if (s.Length == 21)
			{
				try
				{
					var year = int.Parse(s.Substring(0, 4));
					var month = int.Parse(s.Substring(4, 2));
					var day = int.Parse(s.Substring(6, 2));
					var hour = int.Parse(s.Substring(8, 2));
					var minute = int.Parse(s.Substring(10, 2));
					var second = int.Parse(s.Substring(12, 2));
					var millisecond = int.Parse(s.Substring(15, 3));
					return new DateTime(year, month, day, hour, minute, second, millisecond, DateTimeKind.Utc);
				}
				catch (Exception)
				{
					return DateTime.MaxValue;
				}
			}
			return DateTime.MaxValue;
		}

		private DateTime ParseTimestampInFileName(string fileName)
		{
			var split = fileName.Split('_');
			for (int i = 0; i < split.Length; i++)
			{
				// This assumes 2016 survey data...
				var s = split[i];
				if (s.StartsWith("16") && s.Length == 6)
				{
					return ParseTimestamp(s + "_" + split[i + 1]);
				}
				else if (s.StartsWith("2016") && s.Length == 21)
				{
					return ParseTimestamp(s);
				}
			}
			return DateTime.MaxValue;
		}

		private void EnumerateImageFiles(string[] filePaths)
		{
			foreach (var filePath in filePaths)
			{
				var imageFile = new ImageFile();
				imageFile.Path = filePath;
				imageFile.Type = filePath.Contains("COLOR") ? ImageType.Color : (filePath.Contains("THERM") ? ImageType.Thermal : ImageType.Unknown);
				imageFile.Timestamp = ParseTimestampInFileName(Path.GetFileName(filePath));
				imageFile.SizeInBytes = new FileInfo(filePath).Length;
				var key = String.Format("{0}-{1:00}-{2:00}", imageFile.Timestamp.Year, imageFile.Timestamp.Month, imageFile.Timestamp.Day);
				List<ImageFile> list = null;
				if (!_imagesByDateString.TryGetValue(key, out list))
				{
					list = new List<ImageFile>();
					_imagesByDateString[key] = list;
				}
				list.Add(imageFile);
				if (_pathsExamined++ % 1000 == 0)
				{
					UpdateImageFileStatsLabels();
				}
			}
		}

		private void EnumerateImageFilesInDir(string path)
		{
			EnumerateImageFiles(Directory.GetFiles(path, "*.PNG"));
			EnumerateImageFiles(Directory.GetFiles(path, "*.JPG"));

			foreach (var subDir in Directory.GetDirectories(path).Where(x => !x.Contains("System Volume Information")))
			{
				EnumerateImageFilesInDir(subDir);
			}
		}

		private Tuple<int, long> GetImageFileStats(ImageType type, string dateFilter = null, List<ImageFile> queue = null)
		{
			int totalImageCount = 0;
			long totalSizeInBytes = 0;
			foreach (var list in _imagesByDateString.Where(kvp => dateFilter == null || kvp.Key == dateFilter))
			{
				foreach (var image in list.Value.Where(image => image.Type == type))
				{
					totalImageCount++;
					totalSizeInBytes += image.SizeInBytes;
					if (queue != null)
						queue.Add(image);
				}
			}
			return Tuple.Create(totalImageCount, totalSizeInBytes);
		}
		
		private void UpdateImageFileStatsLabels()
		{
			var thermalStats = GetImageFileStats(ImageType.Thermal);
			sourceThermalFileInfo.Text = String.Format("{0} thermal images ({1:0.0} GB)", thermalStats.Item1, thermalStats.Item2 / BytesPerGB);

			var colorStats = GetImageFileStats(ImageType.Color);
			sourceColorFileInfo.Text = String.Format("{0} color images ({1:0.0} GB)", colorStats.Item1, colorStats.Item2 / BytesPerGB);

			var unknownStats = GetImageFileStats(ImageType.Unknown);
			sourceUnknownFileInfo.Text = String.Format("{0} unknown images ({1:0.0} GB)", unknownStats.Item1, unknownStats.Item2 / BytesPerGB);

			this.Refresh();
		}

		private void UpdateDateList()
		{
			datesListBox.Items.Clear();
			var keys = _imagesByDateString.Keys.ToList();
			keys.Sort();
			foreach (var key in keys)
			{
				datesListBox.Items.Add(key);
			}
		}

		private void UpdateSelectionInfo()
		{
			int totalImageCount = 0;
			long totalSizeInBytes = 0;
			_copyQueue.Clear();

			foreach (var dateFilter in datesListBox.SelectedItems)
			{
				if (copyThermalImagesCheckBox.Checked)
				{
					var stats = GetImageFileStats(ImageType.Thermal, (string)dateFilter, _copyQueue);
					totalImageCount += stats.Item1;
					totalSizeInBytes += stats.Item2;
				}
				if (copyColorImagesCheckBox.Checked)
				{
					var stats = GetImageFileStats(ImageType.Color, (string)dateFilter, _copyQueue);
					totalImageCount += stats.Item1;
					totalSizeInBytes += stats.Item2;
				}
				if (copyUnknownImagesCheckBox.Checked)
				{
					var stats = GetImageFileStats(ImageType.Unknown, (string)dateFilter, _copyQueue);
					totalImageCount += stats.Item1;
					totalSizeInBytes += stats.Item2;
				}
			}

			selectionInfoLabel.Text = String.Format("{0} selected images ({1:0.0} GB)", totalImageCount, totalSizeInBytes / BytesPerGB);
		}

		private void UpdateCopyStats()
		{
			imagesCopiedLabel.Text = String.Format("{0} images {3} ({1:0.0} GB) with {2} errors", _imagesCopied, _bytesCopied / BytesPerGB, _copyErrors.Count, this.moveCheckBox.Checked ? "moved" : "copied");

			this.Refresh();
		}

		private void Form1_Load(object sender, EventArgs e)
		{
		}

		private void pickSourceButton_Click(object sender, EventArgs e)
		{
			_imagesByDateString.Clear();
			_pathsExamined = 0;
			var dialog = new FolderBrowserDialog();
			var result = dialog.ShowDialog();
			if (result == DialogResult.OK)
			{
				this.Enabled = false;
				sourceTextBox.Text = dialog.SelectedPath;
				EnumerateImageFilesInDir(dialog.SelectedPath);
				this.Enabled = true;
				UpdateImageFileStatsLabels();
				UpdateDateList();
			}
		}

		private void pickTargetButton_Click(object sender, EventArgs e)
		{
			var dialog = new FolderBrowserDialog();
			var result = dialog.ShowDialog();
			if (result == DialogResult.OK)
			{
				targetTextBox.Text = dialog.SelectedPath;
			}
		}

		private void datesListBox_SelectedIndexChanged(object sender, EventArgs e)
		{
			UpdateSelectionInfo();
		}

		private void copyThermalImagesCheckBox_CheckedChanged(object sender, EventArgs e)
		{
			UpdateSelectionInfo();
		}

		private void copyColorImagesCheckBox_CheckedChanged(object sender, EventArgs e)
		{
			UpdateSelectionInfo();
		}

		private void copyUnknownImagesCheckBox_CheckedChanged(object sender, EventArgs e)
		{
			UpdateSelectionInfo();
		}

		private void startCopyButton_Click(object sender, EventArgs e)
		{
			_imagesCopied = 0;
			_bytesCopied = 0;
			_copyErrors.Clear();

			this.Enabled = false;
			foreach (var image in _copyQueue)
			{
				try
				{
					var targetPath = Path.Combine(targetTextBox.Text, Path.GetFileName(image.Path));
					if (!File.Exists(targetPath))
					{
						if (this.moveCheckBox.Checked)
						{
							File.Move(image.Path, targetPath);
						}
						else
						{
							File.Copy(image.Path, targetPath);
						}
					}
				}
				catch (Exception)
				{
					_copyErrors.Add(image);
				}

				_imagesCopied++;
				_bytesCopied += image.SizeInBytes;

				if (_imagesCopied % 100 == 0)
				{
					UpdateCopyStats();
				}
			}
			UpdateCopyStats();
			this.Enabled = true;
		}
	}
}
