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

using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.IO;

namespace BISE
{
    public partial class frmProjectProperties : Form
    {
        int _frameStart;
        int _frameEnd;
        string _sourceDir;
        string _outputDir;
        string _outputFilenameRoot;
        string _projectDirectory;

        public int frameStart
        {
            get { return _frameStart; }
            set { _frameStart = value; }
        }

        public int frameEnd
        {
            get { return _frameEnd; }
            set { _frameEnd = value; }
        }

        public string sourceDir
        {
            get { return _sourceDir; }
            set { _sourceDir = value; }
        }

        public string outputDir
        {
            get { return _outputDir; }
            set { _outputDir = value; }
        }

        public string outputFilenameRoot
        {
            get { return _outputFilenameRoot; }
            set { _outputFilenameRoot = value; }
        }

        public string projectDirectory
        {
            set { _projectDirectory = value; }
        }

        public frmProjectProperties()
        {            
            this.DialogResult = DialogResult.Cancel;
            InitializeComponent();
        }

        private void frmProjectProperties_Load(object sender, EventArgs e)
        {
            nudFrameStart.Value = _frameStart;
            nudFrameEnd.Value = _frameEnd;
            txtSourceDir.Text = _sourceDir;
            txtOutputDir.Text = _outputDir;
            txtOutputFilenameRoot.Text = _outputFilenameRoot;
        }

        private void btnCancel_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void btnOK_Click(object sender, EventArgs e)
        {
            _frameStart = Convert.ToInt32(nudFrameStart.Value);
            _frameEnd = Convert.ToInt32(nudFrameEnd.Value); 
            _sourceDir = txtSourceDir.Text;
            _outputDir = txtOutputDir.Text;
            _outputFilenameRoot = txtOutputFilenameRoot.Text;

            this.DialogResult = DialogResult.OK;
            this.Close();
        }

        /// <summary>
        /// Creates a relative path from one file or folder to another.
        /// </summary>
        /// <param name="fromPath">Contains the directory that defines the start of the relative path.</param>
        /// <param name="toPath">Contains the path that defines the endpoint of the relative path.</param>
        /// <returns>The relative path from the start directory to the end path.</returns>
        /// <exception cref="ArgumentNullException"></exception>
        /// <exception cref="UriFormatException"></exception>
        /// <exception cref="InvalidOperationException"></exception>
        public static String MakeRelativePath(String fromPath, String toPath)
        {
            if (String.IsNullOrEmpty(fromPath)) throw new ArgumentNullException("fromPath");
            if (String.IsNullOrEmpty(toPath)) throw new ArgumentNullException("toPath");

            Uri fromUri = new Uri(fromPath);
            Uri toUri = new Uri(toPath);

            if (fromUri.Scheme != toUri.Scheme) { return toPath; } // path can't be made relative.

            Uri relativeUri = fromUri.MakeRelativeUri(toUri);
            String relativePath = Uri.UnescapeDataString(relativeUri.ToString());

            if (toUri.Scheme.ToUpperInvariant() == "FILE")
            {
                relativePath = relativePath.Replace(Path.AltDirectorySeparatorChar, Path.DirectorySeparatorChar);
            }

            return relativePath;
        }

        private void btnSourceDir_Click(object sender, EventArgs e)
        {
            FolderBrowserDialog folderBrowserDialog1 = new FolderBrowserDialog();
            if (folderBrowserDialog1.ShowDialog() == DialogResult.OK)
            {
                txtSourceDir.Text = MakeRelativePath(_projectDirectory + @"\", folderBrowserDialog1.SelectedPath + @"\");
            }
        }

        private void btnOutputDir_Click(object sender, EventArgs e)
        {
            FolderBrowserDialog folderBrowserDialog1 = new FolderBrowserDialog();
            if (folderBrowserDialog1.ShowDialog() == DialogResult.OK)
            {
                txtOutputDir.Text = MakeRelativePath(_projectDirectory + @"\", folderBrowserDialog1.SelectedPath + @"\");
            }
        }
    }
}
