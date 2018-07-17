namespace CopyImageFiles
{
	partial class Form1
	{
		/// <summary>
		/// Required designer variable.
		/// </summary>
		private System.ComponentModel.IContainer components = null;

		/// <summary>
		/// Clean up any resources being used.
		/// </summary>
		/// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
		protected override void Dispose(bool disposing)
		{
			if (disposing && (components != null))
			{
				components.Dispose();
			}
			base.Dispose(disposing);
		}

		#region Windows Form Designer generated code

		/// <summary>
		/// Required method for Designer support - do not modify
		/// the contents of this method with the code editor.
		/// </summary>
		private void InitializeComponent()
		{
			this.label1 = new System.Windows.Forms.Label();
			this.pickSourceButton = new System.Windows.Forms.Button();
			this.sourceTextBox = new System.Windows.Forms.TextBox();
			this.targetTextBox = new System.Windows.Forms.TextBox();
			this.pickTargetButton = new System.Windows.Forms.Button();
			this.label2 = new System.Windows.Forms.Label();
			this.sourceThermalFileInfo = new System.Windows.Forms.Label();
			this.sourceColorFileInfo = new System.Windows.Forms.Label();
			this.datesListBox = new System.Windows.Forms.ListBox();
			this.label3 = new System.Windows.Forms.Label();
			this.copyThermalImagesCheckBox = new System.Windows.Forms.CheckBox();
			this.copyColorImagesCheckBox = new System.Windows.Forms.CheckBox();
			this.selectionInfoLabel = new System.Windows.Forms.Label();
			this.sourceUnknownFileInfo = new System.Windows.Forms.Label();
			this.copyUnknownImagesCheckBox = new System.Windows.Forms.CheckBox();
			this.imagesCopiedLabel = new System.Windows.Forms.Label();
			this.startCopyButton = new System.Windows.Forms.Button();
			this.moveCheckBox = new System.Windows.Forms.CheckBox();
			this.SuspendLayout();
			// 
			// label1
			// 
			this.label1.AutoSize = true;
			this.label1.Location = new System.Drawing.Point(13, 13);
			this.label1.Name = "label1";
			this.label1.Size = new System.Drawing.Size(86, 13);
			this.label1.TabIndex = 0;
			this.label1.Text = "Source Root Dir:";
			// 
			// pickSourceButton
			// 
			this.pickSourceButton.Location = new System.Drawing.Point(366, 8);
			this.pickSourceButton.Name = "pickSourceButton";
			this.pickSourceButton.Size = new System.Drawing.Size(75, 23);
			this.pickSourceButton.TabIndex = 1;
			this.pickSourceButton.Text = "Browse...";
			this.pickSourceButton.UseVisualStyleBackColor = true;
			this.pickSourceButton.Click += new System.EventHandler(this.pickSourceButton_Click);
			// 
			// sourceTextBox
			// 
			this.sourceTextBox.Location = new System.Drawing.Point(105, 10);
			this.sourceTextBox.Name = "sourceTextBox";
			this.sourceTextBox.ReadOnly = true;
			this.sourceTextBox.Size = new System.Drawing.Size(255, 20);
			this.sourceTextBox.TabIndex = 2;
			// 
			// targetTextBox
			// 
			this.targetTextBox.Location = new System.Drawing.Point(105, 230);
			this.targetTextBox.Name = "targetTextBox";
			this.targetTextBox.ReadOnly = true;
			this.targetTextBox.Size = new System.Drawing.Size(255, 20);
			this.targetTextBox.TabIndex = 5;
			// 
			// pickTargetButton
			// 
			this.pickTargetButton.Location = new System.Drawing.Point(366, 228);
			this.pickTargetButton.Name = "pickTargetButton";
			this.pickTargetButton.Size = new System.Drawing.Size(75, 23);
			this.pickTargetButton.TabIndex = 4;
			this.pickTargetButton.Text = "Browse...";
			this.pickTargetButton.UseVisualStyleBackColor = true;
			this.pickTargetButton.Click += new System.EventHandler(this.pickTargetButton_Click);
			// 
			// label2
			// 
			this.label2.AutoSize = true;
			this.label2.Location = new System.Drawing.Point(13, 233);
			this.label2.Name = "label2";
			this.label2.Size = new System.Drawing.Size(57, 13);
			this.label2.TabIndex = 3;
			this.label2.Text = "Target Dir:";
			// 
			// sourceThermalFileInfo
			// 
			this.sourceThermalFileInfo.AutoSize = true;
			this.sourceThermalFileInfo.Location = new System.Drawing.Point(16, 40);
			this.sourceThermalFileInfo.Name = "sourceThermalFileInfo";
			this.sourceThermalFileInfo.Size = new System.Drawing.Size(86, 13);
			this.sourceThermalFileInfo.TabIndex = 6;
			this.sourceThermalFileInfo.Text = "0 thermal images";
			// 
			// sourceColorFileInfo
			// 
			this.sourceColorFileInfo.AutoSize = true;
			this.sourceColorFileInfo.Location = new System.Drawing.Point(16, 64);
			this.sourceColorFileInfo.Name = "sourceColorFileInfo";
			this.sourceColorFileInfo.Size = new System.Drawing.Size(75, 13);
			this.sourceColorFileInfo.TabIndex = 9;
			this.sourceColorFileInfo.Text = "0 color images";
			// 
			// datesListBox
			// 
			this.datesListBox.FormattingEnabled = true;
			this.datesListBox.Location = new System.Drawing.Point(204, 58);
			this.datesListBox.Name = "datesListBox";
			this.datesListBox.SelectionMode = System.Windows.Forms.SelectionMode.MultiExtended;
			this.datesListBox.Size = new System.Drawing.Size(130, 108);
			this.datesListBox.TabIndex = 10;
			this.datesListBox.SelectedIndexChanged += new System.EventHandler(this.datesListBox_SelectedIndexChanged);
			// 
			// label3
			// 
			this.label3.AutoSize = true;
			this.label3.Location = new System.Drawing.Point(201, 40);
			this.label3.Name = "label3";
			this.label3.Size = new System.Drawing.Size(83, 13);
			this.label3.TabIndex = 11;
			this.label3.Text = "Selected Dates:";
			// 
			// copyThermalImagesCheckBox
			// 
			this.copyThermalImagesCheckBox.AutoSize = true;
			this.copyThermalImagesCheckBox.Checked = true;
			this.copyThermalImagesCheckBox.CheckState = System.Windows.Forms.CheckState.Checked;
			this.copyThermalImagesCheckBox.Location = new System.Drawing.Point(19, 126);
			this.copyThermalImagesCheckBox.Name = "copyThermalImagesCheckBox";
			this.copyThermalImagesCheckBox.Size = new System.Drawing.Size(123, 17);
			this.copyThermalImagesCheckBox.TabIndex = 12;
			this.copyThermalImagesCheckBox.Text = "Copy thermal images";
			this.copyThermalImagesCheckBox.UseVisualStyleBackColor = true;
			this.copyThermalImagesCheckBox.CheckedChanged += new System.EventHandler(this.copyThermalImagesCheckBox_CheckedChanged);
			// 
			// copyColorImagesCheckBox
			// 
			this.copyColorImagesCheckBox.AutoSize = true;
			this.copyColorImagesCheckBox.Checked = true;
			this.copyColorImagesCheckBox.CheckState = System.Windows.Forms.CheckState.Checked;
			this.copyColorImagesCheckBox.Location = new System.Drawing.Point(19, 149);
			this.copyColorImagesCheckBox.Name = "copyColorImagesCheckBox";
			this.copyColorImagesCheckBox.Size = new System.Drawing.Size(112, 17);
			this.copyColorImagesCheckBox.TabIndex = 13;
			this.copyColorImagesCheckBox.Text = "Copy color images";
			this.copyColorImagesCheckBox.UseVisualStyleBackColor = true;
			this.copyColorImagesCheckBox.CheckedChanged += new System.EventHandler(this.copyColorImagesCheckBox_CheckedChanged);
			// 
			// selectionInfoLabel
			// 
			this.selectionInfoLabel.AutoSize = true;
			this.selectionInfoLabel.Location = new System.Drawing.Point(201, 173);
			this.selectionInfoLabel.Name = "selectionInfoLabel";
			this.selectionInfoLabel.Size = new System.Drawing.Size(92, 13);
			this.selectionInfoLabel.TabIndex = 14;
			this.selectionInfoLabel.Text = "0 images selected";
			// 
			// sourceUnknownFileInfo
			// 
			this.sourceUnknownFileInfo.AutoSize = true;
			this.sourceUnknownFileInfo.Location = new System.Drawing.Point(16, 90);
			this.sourceUnknownFileInfo.Name = "sourceUnknownFileInfo";
			this.sourceUnknownFileInfo.Size = new System.Drawing.Size(96, 13);
			this.sourceUnknownFileInfo.TabIndex = 15;
			this.sourceUnknownFileInfo.Text = "0 unknown images";
			// 
			// copyUnknownImagesCheckBox
			// 
			this.copyUnknownImagesCheckBox.AutoSize = true;
			this.copyUnknownImagesCheckBox.Location = new System.Drawing.Point(19, 172);
			this.copyUnknownImagesCheckBox.Name = "copyUnknownImagesCheckBox";
			this.copyUnknownImagesCheckBox.Size = new System.Drawing.Size(133, 17);
			this.copyUnknownImagesCheckBox.TabIndex = 16;
			this.copyUnknownImagesCheckBox.Text = "Copy unknown images";
			this.copyUnknownImagesCheckBox.UseVisualStyleBackColor = true;
			this.copyUnknownImagesCheckBox.CheckedChanged += new System.EventHandler(this.copyUnknownImagesCheckBox_CheckedChanged);
			// 
			// imagesCopiedLabel
			// 
			this.imagesCopiedLabel.AutoSize = true;
			this.imagesCopiedLabel.Location = new System.Drawing.Point(16, 266);
			this.imagesCopiedLabel.Name = "imagesCopiedLabel";
			this.imagesCopiedLabel.Size = new System.Drawing.Size(84, 13);
			this.imagesCopiedLabel.TabIndex = 17;
			this.imagesCopiedLabel.Text = "0 images copied";
			// 
			// startCopyButton
			// 
			this.startCopyButton.Location = new System.Drawing.Point(321, 261);
			this.startCopyButton.Name = "startCopyButton";
			this.startCopyButton.Size = new System.Drawing.Size(120, 23);
			this.startCopyButton.TabIndex = 18;
			this.startCopyButton.Text = "GO!";
			this.startCopyButton.UseVisualStyleBackColor = true;
			this.startCopyButton.Click += new System.EventHandler(this.startCopyButton_Click);
			// 
			// moveCheckBox
			// 
			this.moveCheckBox.AutoSize = true;
			this.moveCheckBox.Location = new System.Drawing.Point(19, 195);
			this.moveCheckBox.Name = "moveCheckBox";
			this.moveCheckBox.Size = new System.Drawing.Size(162, 17);
			this.moveCheckBox.TabIndex = 19;
			this.moveCheckBox.Text = "Move images (delete source)";
			this.moveCheckBox.UseVisualStyleBackColor = true;
			// 
			// Form1
			// 
			this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
			this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
			this.ClientSize = new System.Drawing.Size(456, 300);
			this.Controls.Add(this.moveCheckBox);
			this.Controls.Add(this.startCopyButton);
			this.Controls.Add(this.imagesCopiedLabel);
			this.Controls.Add(this.copyUnknownImagesCheckBox);
			this.Controls.Add(this.sourceUnknownFileInfo);
			this.Controls.Add(this.selectionInfoLabel);
			this.Controls.Add(this.copyColorImagesCheckBox);
			this.Controls.Add(this.copyThermalImagesCheckBox);
			this.Controls.Add(this.label3);
			this.Controls.Add(this.datesListBox);
			this.Controls.Add(this.sourceColorFileInfo);
			this.Controls.Add(this.sourceThermalFileInfo);
			this.Controls.Add(this.targetTextBox);
			this.Controls.Add(this.pickTargetButton);
			this.Controls.Add(this.label2);
			this.Controls.Add(this.sourceTextBox);
			this.Controls.Add(this.pickSourceButton);
			this.Controls.Add(this.label1);
			this.Name = "Form1";
			this.Text = "Copy Arctic Seals Image Files";
			this.Load += new System.EventHandler(this.Form1_Load);
			this.ResumeLayout(false);
			this.PerformLayout();

		}

		#endregion

		private System.Windows.Forms.Label label1;
		private System.Windows.Forms.Button pickSourceButton;
		private System.Windows.Forms.TextBox sourceTextBox;
		private System.Windows.Forms.TextBox targetTextBox;
		private System.Windows.Forms.Button pickTargetButton;
		private System.Windows.Forms.Label label2;
		private System.Windows.Forms.Label sourceThermalFileInfo;
		private System.Windows.Forms.Label sourceColorFileInfo;
		private System.Windows.Forms.ListBox datesListBox;
		private System.Windows.Forms.Label label3;
		private System.Windows.Forms.CheckBox copyThermalImagesCheckBox;
		private System.Windows.Forms.CheckBox copyColorImagesCheckBox;
		private System.Windows.Forms.Label selectionInfoLabel;
		private System.Windows.Forms.Label sourceUnknownFileInfo;
		private System.Windows.Forms.CheckBox copyUnknownImagesCheckBox;
		private System.Windows.Forms.Label imagesCopiedLabel;
		private System.Windows.Forms.Button startCopyButton;
		private System.Windows.Forms.CheckBox moveCheckBox;
	}
}

