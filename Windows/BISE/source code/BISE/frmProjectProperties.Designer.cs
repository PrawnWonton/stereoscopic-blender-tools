/*
* ##### BEGIN GPL LICENSE BLOCK #####
*
*  This program is free software; you can redistribute it and/or
*  modify it under the terms of the GNU General Public License
*  as published by the Free Software Foundation; either version 2
*  of the License, or (at your option) any later version.
*
*  This program is distributed in the hope that it will be useful,
*  but WITHOUT ANY WARRANTY; without even the implied warranty of
*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*  GNU General Public License for more details.
*
*  You should have received a copy of the GNU General Public License
*  along with this program; if not, write to the Free Software Foundation,
*  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
*
* ##### END GPL LICENSE BLOCK #####
*/

namespace BISE
{
    partial class frmProjectProperties
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
            this.btnOK = new System.Windows.Forms.Button();
            this.btnCancel = new System.Windows.Forms.Button();
            this.groupBox1 = new System.Windows.Forms.GroupBox();
            this.label1 = new System.Windows.Forms.Label();
            this.nudFrameEnd = new System.Windows.Forms.NumericUpDown();
            this.label2 = new System.Windows.Forms.Label();
            this.nudFrameStart = new System.Windows.Forms.NumericUpDown();
            this.label3 = new System.Windows.Forms.Label();
            this.label4 = new System.Windows.Forms.Label();
            this.label5 = new System.Windows.Forms.Label();
            this.txtSourceDir = new System.Windows.Forms.TextBox();
            this.txtOutputDir = new System.Windows.Forms.TextBox();
            this.txtOutputFilenameRoot = new System.Windows.Forms.TextBox();
            this.btnSourceDir = new System.Windows.Forms.Button();
            this.btnOutputDir = new System.Windows.Forms.Button();
            this.groupBox1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.nudFrameEnd)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.nudFrameStart)).BeginInit();
            this.SuspendLayout();
            // 
            // btnOK
            // 
            this.btnOK.Anchor = System.Windows.Forms.AnchorStyles.Bottom;
            this.btnOK.Location = new System.Drawing.Point(232, 212);
            this.btnOK.Name = "btnOK";
            this.btnOK.Size = new System.Drawing.Size(75, 23);
            this.btnOK.TabIndex = 13;
            this.btnOK.Text = "OK";
            this.btnOK.UseVisualStyleBackColor = true;
            this.btnOK.Click += new System.EventHandler(this.btnOK_Click);
            // 
            // btnCancel
            // 
            this.btnCancel.Anchor = System.Windows.Forms.AnchorStyles.Bottom;
            this.btnCancel.DialogResult = System.Windows.Forms.DialogResult.Cancel;
            this.btnCancel.Location = new System.Drawing.Point(322, 212);
            this.btnCancel.Name = "btnCancel";
            this.btnCancel.Size = new System.Drawing.Size(75, 23);
            this.btnCancel.TabIndex = 14;
            this.btnCancel.Text = "Cancel";
            this.btnCancel.UseVisualStyleBackColor = true;
            this.btnCancel.Click += new System.EventHandler(this.btnCancel_Click);
            // 
            // groupBox1
            // 
            this.groupBox1.Controls.Add(this.label1);
            this.groupBox1.Controls.Add(this.nudFrameEnd);
            this.groupBox1.Controls.Add(this.label2);
            this.groupBox1.Controls.Add(this.nudFrameStart);
            this.groupBox1.Location = new System.Drawing.Point(154, 33);
            this.groupBox1.Name = "groupBox1";
            this.groupBox1.Size = new System.Drawing.Size(299, 51);
            this.groupBox1.TabIndex = 0;
            this.groupBox1.TabStop = false;
            this.groupBox1.Text = "Frames";
            // 
            // label1
            // 
            this.label1.Location = new System.Drawing.Point(160, 21);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(66, 18);
            this.label1.TabIndex = 3;
            this.label1.Text = "&End:";
            this.label1.TextAlign = System.Drawing.ContentAlignment.TopRight;
            // 
            // nudFrameEnd
            // 
            this.nudFrameEnd.Location = new System.Drawing.Point(232, 19);
            this.nudFrameEnd.Maximum = new decimal(new int[] {
            9999,
            0,
            0,
            0});
            this.nudFrameEnd.Minimum = new decimal(new int[] {
            1,
            0,
            0,
            0});
            this.nudFrameEnd.Name = "nudFrameEnd";
            this.nudFrameEnd.Size = new System.Drawing.Size(55, 20);
            this.nudFrameEnd.TabIndex = 4;
            this.nudFrameEnd.Value = new decimal(new int[] {
            1,
            0,
            0,
            0});
            // 
            // label2
            // 
            this.label2.Location = new System.Drawing.Point(11, 21);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(66, 18);
            this.label2.TabIndex = 1;
            this.label2.Text = "&Start:";
            this.label2.TextAlign = System.Drawing.ContentAlignment.TopRight;
            // 
            // nudFrameStart
            // 
            this.nudFrameStart.Location = new System.Drawing.Point(83, 19);
            this.nudFrameStart.Maximum = new decimal(new int[] {
            9999,
            0,
            0,
            0});
            this.nudFrameStart.Minimum = new decimal(new int[] {
            1,
            0,
            0,
            0});
            this.nudFrameStart.Name = "nudFrameStart";
            this.nudFrameStart.Size = new System.Drawing.Size(55, 20);
            this.nudFrameStart.TabIndex = 2;
            this.nudFrameStart.Value = new decimal(new int[] {
            1,
            0,
            0,
            0});
            // 
            // label3
            // 
            this.label3.Location = new System.Drawing.Point(82, 93);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(66, 18);
            this.label3.TabIndex = 5;
            this.label3.Text = "Source &Dir:";
            this.label3.TextAlign = System.Drawing.ContentAlignment.TopRight;
            // 
            // label4
            // 
            this.label4.Location = new System.Drawing.Point(82, 119);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(66, 18);
            this.label4.TabIndex = 8;
            this.label4.Text = "&Output Dir:";
            this.label4.TextAlign = System.Drawing.ContentAlignment.TopRight;
            // 
            // label5
            // 
            this.label5.Location = new System.Drawing.Point(15, 145);
            this.label5.Name = "label5";
            this.label5.Size = new System.Drawing.Size(133, 18);
            this.label5.TabIndex = 11;
            this.label5.Text = "Output Filename &Root:";
            this.label5.TextAlign = System.Drawing.ContentAlignment.TopRight;
            // 
            // txtSourceDir
            // 
            this.txtSourceDir.Location = new System.Drawing.Point(154, 90);
            this.txtSourceDir.Name = "txtSourceDir";
            this.txtSourceDir.Size = new System.Drawing.Size(401, 20);
            this.txtSourceDir.TabIndex = 6;
            // 
            // txtOutputDir
            // 
            this.txtOutputDir.Location = new System.Drawing.Point(154, 116);
            this.txtOutputDir.Name = "txtOutputDir";
            this.txtOutputDir.Size = new System.Drawing.Size(401, 20);
            this.txtOutputDir.TabIndex = 9;
            // 
            // txtOutputFilenameRoot
            // 
            this.txtOutputFilenameRoot.Location = new System.Drawing.Point(154, 142);
            this.txtOutputFilenameRoot.Name = "txtOutputFilenameRoot";
            this.txtOutputFilenameRoot.Size = new System.Drawing.Size(125, 20);
            this.txtOutputFilenameRoot.TabIndex = 12;
            // 
            // btnSourceDir
            // 
            this.btnSourceDir.Location = new System.Drawing.Point(561, 90);
            this.btnSourceDir.Name = "btnSourceDir";
            this.btnSourceDir.Size = new System.Drawing.Size(25, 21);
            this.btnSourceDir.TabIndex = 7;
            this.btnSourceDir.Text = "...";
            this.btnSourceDir.UseVisualStyleBackColor = true;
            this.btnSourceDir.Click += new System.EventHandler(this.btnSourceDir_Click);
            // 
            // btnOutputDir
            // 
            this.btnOutputDir.Location = new System.Drawing.Point(561, 116);
            this.btnOutputDir.Name = "btnOutputDir";
            this.btnOutputDir.Size = new System.Drawing.Size(25, 21);
            this.btnOutputDir.TabIndex = 10;
            this.btnOutputDir.Text = "...";
            this.btnOutputDir.UseVisualStyleBackColor = true;
            this.btnOutputDir.Click += new System.EventHandler(this.btnOutputDir_Click);
            // 
            // frmProjectProperties
            // 
            this.AcceptButton = this.btnOK;
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.CancelButton = this.btnCancel;
            this.ClientSize = new System.Drawing.Size(603, 247);
            this.Controls.Add(this.btnOutputDir);
            this.Controls.Add(this.btnSourceDir);
            this.Controls.Add(this.txtOutputFilenameRoot);
            this.Controls.Add(this.txtOutputDir);
            this.Controls.Add(this.txtSourceDir);
            this.Controls.Add(this.label5);
            this.Controls.Add(this.label4);
            this.Controls.Add(this.label3);
            this.Controls.Add(this.groupBox1);
            this.Controls.Add(this.btnCancel);
            this.Controls.Add(this.btnOK);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "frmProjectProperties";
            this.ShowInTaskbar = false;
            this.SizeGripStyle = System.Windows.Forms.SizeGripStyle.Hide;
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
            this.Text = "Project Properties";
            this.Load += new System.EventHandler(this.frmProjectProperties_Load);
            this.groupBox1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.nudFrameEnd)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.nudFrameStart)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Button btnOK;
        private System.Windows.Forms.Button btnCancel;
        private System.Windows.Forms.GroupBox groupBox1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.NumericUpDown nudFrameStart;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.NumericUpDown nudFrameEnd;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.Label label5;
        private System.Windows.Forms.TextBox txtSourceDir;
        private System.Windows.Forms.TextBox txtOutputDir;
        private System.Windows.Forms.TextBox txtOutputFilenameRoot;
        private System.Windows.Forms.Button btnSourceDir;
        private System.Windows.Forms.Button btnOutputDir;
    }
}