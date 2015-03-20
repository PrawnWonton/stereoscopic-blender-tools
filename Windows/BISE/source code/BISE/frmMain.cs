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
using System.Reflection;
using System.Resources;
using Microsoft.Win32;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
using JWC;

namespace BISE
{
    public partial class frmMain : Form
    {

        public struct frameInfo
        {
            public int frameNum;
            public string fileName;
        }

        int _frameStart = 1;
        int _frameEnd = 100;
        int _multiRate = 1;
        List<frameInfo> _frameList = new List<frameInfo>();
        string _sourceDir = "";
        string _outputDir = "";
        string _outputFilenameRoot = "";
        bool _projectDirty = false;
        string _projectFilename = "";
        string _projectDirectory = "";
        string _automaticFileToLoad = "";

        protected MruStripMenu mruMenu;
        static string mruRegKey = "SOFTWARE\\BISE";
        protected string curFileName;
        private int m_curFileNum = 0;

        public frmMain(string openFile)
        {
            InitializeComponent();
            this.AllowDrop = true;
            this.DragEnter += new DragEventHandler(frmMain_DragEnter);
            this.DragDrop += new DragEventHandler(frmMain_DragDrop);
            _automaticFileToLoad = openFile;

            RegistryKey regKey = Registry.CurrentUser.OpenSubKey(mruRegKey);
            mruMenu = new MruStripMenu(mnuRecentFiles, new MruStripMenu.ClickedHandler(OnMruFile), mruRegKey + "\\MRU", 16);
            mruMenu.LoadFromRegistry();
            IncFilename();
        }

        private void saveToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (!File.Exists(_projectFilename))
            {
                SaveAs();
                return;
            }
            else
            {
                SaveProject();
            }
        }

        private void exitToolStripMenuItem_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void frmMain_Load(object sender, EventArgs e)
        {
            LoadNewProjectDefaults();
            toolStripProgressBar1.Visible = false;
            toolStripStatusLabel1.Text = "Ready";

            RefreshList();
            MarkProjectClean();

            if (_automaticFileToLoad.Length > 0)
            {
                _projectFilename = _automaticFileToLoad;
                OpenProject();
            }
        }

        private void InsertFrame(int newFrameNum, string newFileName)
        {
            // Does this frame exist?
            int i = _frameList.FindIndex(c => c.frameNum == newFrameNum);

            frameInfo fi = new frameInfo();
            fi.frameNum = newFrameNum;
            fi.fileName = newFileName;

            if (i>=0)
            {
                _frameList[i] = fi;
            }
            else
            {
                _frameList.Add(fi);
            }

            MarkProjectDirty();
        }

        private void ClearFrame(int deleteFrameNum)
        {
            // Does this frame exist?
            int i = _frameList.FindIndex(c => c.frameNum == deleteFrameNum);

            if (i >= 0)
            {
                _frameList.RemoveAt(i);
                MarkProjectDirty();
            }
        }

        private void RefreshList()
        {
            int frameToHighlight = lbProject.SelectedIndex;

            lbProject.Items.Clear();

            bool isEnabled =  !(_projectFilename.Trim().Length == 0);
            splitContainer1.Enabled = isEnabled;
            mnuSaveProject.Enabled = isEnabled;
            mnuSaveProjectAs.Enabled = isEnabled;
            mnuProjectProperties.Enabled = isEnabled;
            mnuBakeSourceAlphaFiles.Enabled = isEnabled;
            mnuRenderImageSequence.Enabled = isEnabled;
            mnuImportImages.Enabled = isEnabled;
            mnuClearImage.Enabled = isEnabled;
            mnuInsertFrame.Enabled = isEnabled;
            mnuDeleteFrame.Enabled = isEnabled;
            mnuMoveImageUp.Enabled = isEnabled;
            mnuMoveImageDown.Enabled = isEnabled;

            if (!isEnabled)
            {
                return;
            }

            string strMostRecentName = "";
            for (int i = _frameStart; i <= _frameEnd; i++)
            {
                frameInfo item = _frameList.Find(c => c.frameNum == i);
                if ((item.frameNum == i) && (item.fileName != null))
                {
                    lbProject.Items.Add(i.ToString("D4") + " " + item.fileName);
                    strMostRecentName = item.fileName;
                }
                else
                {
                    lbProject.Items.Add(i.ToString("D4") + "   (" + strMostRecentName + ")");
                }

            }

            if (frameToHighlight < 0)
            {
                frameToHighlight = 0;
            }
            else if (frameToHighlight > lbProject.Items.Count - 1)
            {
                frameToHighlight = lbProject.Items.Count - 1;
            }
            
            lbProject.SetSelected(frameToHighlight, true);
            
        }

        private void lbProject_SelectedIndexChanged(object sender, EventArgs e)
        {
            int frameToFind = lbProject.SelectedIndex + _frameStart;

            // Figure out what file belongs to that frame.
            frameInfo item = _frameList.Find(c => c.frameNum == frameToFind);
            if ((item.frameNum == frameToFind) && (item.fileName != null))
            {
                // We landed on a keyframe. Load it.
                string strFilename =  Path.Combine(Path.GetDirectoryName(_projectFilename), _sourceDir) + @"\" + item.fileName;
                if (File.Exists(strFilename))
                {
                    pbImage.Image = new Bitmap(strFilename);
                }
                else
                {
                    pbImage.Image = (System.Drawing.Image) Properties.Resources.ImageMissing; 
                }
            }
            else
            {
                // We landed somewhere other than a keyframe. 
                // Work backwards and load the correct thing.
                frameToFind--;
                while (frameToFind >= _frameStart)
                {
                    frameInfo item2 = _frameList.Find(c => c.frameNum == frameToFind);
                    if ((item2.frameNum == frameToFind) && (item2.fileName != null))
                    {
                        // We landed on a keyframe. Load it.
                        string strFilename = Path.Combine(Path.GetDirectoryName(_projectFilename), _sourceDir) + @"\" + item2.fileName;
                        if (File.Exists(strFilename))
                        {
                            pbImage.Image = new Bitmap(strFilename);
                        }
                        else
                        {
                            pbImage.Image = (System.Drawing.Image)Properties.Resources.ImageMissing;
                        }
                        return;
                    }

                    frameToFind--;
                }
                // We landed on the start frame and we have no keyframe there. Therefore, show a blank image.
                pbImage.Image = null;
            }
        }

        private void renderImageSequenceToolStripMenuItem_Click(object sender, EventArgs e)
        {            
            toolStripProgressBar1.Visible = true;
            toolStripProgressBar1.Minimum = _frameStart;
            toolStripProgressBar1.Maximum = _frameEnd;

            // Make our source "alpha" directory if it doesn't exist.
            if (!Directory.Exists(Path.Combine(Path.GetDirectoryName(_projectFilename), _sourceDir) + @"\alpha"))
            {
                Directory.CreateDirectory(Path.Combine(Path.GetDirectoryName(_projectFilename), _sourceDir) + @"\alpha");
            }

            // Make our output "alpha" directory (and output directory!) if it doesn't already exist.
            if (!Directory.Exists(Path.Combine(Path.GetDirectoryName(_projectFilename), _outputDir) + @"\alpha"))
            {
                Directory.CreateDirectory(Path.Combine(Path.GetDirectoryName(_projectFilename), _outputDir) + @"\alpha");
            }

            string strMostRecentName = "";
            for (int i = _frameStart; i <= _frameEnd; i++)
            {
                toolStripProgressBar1.Value = i;   
                frameInfo item = _frameList.Find(c => c.frameNum == i);

                toolStripStatusLabel1.Text = "Writing " + _outputFilenameRoot + " " + i.ToString("D4") + ".png";
                Application.DoEvents();
                if ((item.frameNum == i) && (item.fileName != null))
                {
                    // Make sure there's an alpha for this. If not, we must bake it.
                    if (!DoesFileHaveSourceAlpha(item.fileName))
                    {
                        toolStripStatusLabel1.Text = "Baking source alpha for " + _sourceDir + @"\alpha\" + item.fileName;
                        Application.DoEvents();
                        BakeSourceAlpha(item.fileName);
                        toolStripStatusLabel1.Text = "Writing " + _outputFilenameRoot + " " + i.ToString("D4") + ".png";
                        Application.DoEvents();
                    }

                    File.Copy(Path.Combine(Path.GetDirectoryName(_projectFilename), _sourceDir) + @"\" + item.fileName, Path.Combine(Path.GetDirectoryName(_projectFilename), _outputDir) + @"\" + _outputFilenameRoot + " " + i.ToString("D4") + ".png", true);
                    File.Copy(Path.Combine(Path.GetDirectoryName(_projectFilename), _sourceDir) + @"\alpha\" + item.fileName, Path.Combine(Path.GetDirectoryName(_projectFilename), _outputDir) + @"\alpha\" + _outputFilenameRoot + " " + i.ToString("D4") + ".png", true);
                    strMostRecentName = item.fileName;
                }
                else if (strMostRecentName != "")
                {
                    File.Copy(Path.Combine(Path.GetDirectoryName(_projectFilename), _sourceDir) + @"\" + strMostRecentName, Path.Combine(Path.GetDirectoryName(_projectFilename), _outputDir) + @"\" + _outputFilenameRoot + " " + i.ToString("D4") + ".png", true);
                    File.Copy(Path.Combine(Path.GetDirectoryName(_projectFilename), _sourceDir) + @"\alpha\" + strMostRecentName, Path.Combine(Path.GetDirectoryName(_projectFilename), _outputDir) + @"\alpha\" + _outputFilenameRoot + " " + i.ToString("D4") + ".png", true);
                }
            }

            toolStripStatusLabel1.Text = "Ready";
            MessageBox.Show("Exported image sequence to " + Path.Combine(Path.GetDirectoryName(_projectFilename), _outputDir), "Done!");
            toolStripProgressBar1.Value = _frameStart;
            toolStripProgressBar1.Visible = false;
        }

        private void insertImageToolStripMenuItem_Click(object sender, EventArgs e)
        {
            // Import image(s)
            OpenFileDialog sourceFileOpenFileDialog = new OpenFileDialog();

            sourceFileOpenFileDialog.InitialDirectory = Path.Combine(Path.GetDirectoryName(_projectFilename), _sourceDir); ;
            sourceFileOpenFileDialog.Filter = "PNG Files (*.png)|*.png";
            sourceFileOpenFileDialog.RestoreDirectory = true;
            sourceFileOpenFileDialog.Multiselect = true;
            sourceFileOpenFileDialog.Title = "Please select PNG files for import";

            if (sourceFileOpenFileDialog.ShowDialog() == DialogResult.OK)
            {
                if (sourceFileOpenFileDialog.FileNames.Count() > 1)
                {
                    frmImportMulti fim = new frmImportMulti(_multiRate);
                    if (fim.ShowDialog() != DialogResult.OK)
                    {
                        return;
                    }
                    _multiRate = fim.MultiRate;
                }

                try
                {
                    int frame = lbProject.SelectedIndex + _frameStart;
                    string tempFolder = System.IO.Path.GetTempPath();
                    foreach (string FileName in sourceFileOpenFileDialog.FileNames)
                    {
                        if (Path.GetDirectoryName(FileName).Trim().ToUpper() !=  Path.GetDirectoryName( Path.Combine(Path.GetDirectoryName(_projectFilename), _sourceDir) + @"\").Trim().ToUpper())
                        {
                            throw new Exception("You must pick an image from " +  Path.Combine(Path.GetDirectoryName(_projectFilename), _sourceDir));
                        }

                        InsertFrame(frame, Path.GetFileName(FileName));
                        for (int i = 1; i <= _multiRate; i++)
                        {
                            frame++;

                            if (frame > _frameEnd)
                            {
                                break;
                            }

                            if (i != _multiRate)
                            {
                                ClearFrame(frame);
                            }
                        }
                    }

                    RefreshList();
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
            }
        }

        private void deleteImageToolStripMenuItem_Click(object sender, EventArgs e)
        {
            int frame = lbProject.SelectedIndex + _frameStart;
            ClearFrame(frame);
            RefreshList();
        }

        private void moveDownToolStripMenuItem_Click(object sender, EventArgs e)
        {
            // Move a frame down
            int frameToMove = lbProject.SelectedIndex + _frameStart;
            if ((frameToMove + 1) > _frameEnd)
            {
                return;
            }

            // Does this frame exist?
            int i = _frameList.FindIndex(c => c.frameNum == frameToMove);

            if (i >= 0)
            { 
                // Does the frame after this exist?
                int j = _frameList.FindIndex(c => c.frameNum == (frameToMove + 1));
                if (j >= 0)
                {
                    _frameList.RemoveAt(j); // Remove the old frame.
                    i = _frameList.FindIndex(c => c.frameNum == frameToMove); // Now that we removed the old frame, our i variable may have changed.
                }

                frameInfo fi = new frameInfo();
                fi.frameNum = (frameToMove + 1);
                fi.fileName = _frameList[i].fileName;
                _frameList[i] = fi;
                lbProject.SetSelected(lbProject.SelectedIndex + 1, true);
                MarkProjectDirty();
                RefreshList();
            }
            else
            {
                // We're on an in-between frame, so do nothing
            }
        }

        private void moveUpToolStripMenuItem_Click(object sender, EventArgs e)
        {
            // Move a frame up
            int frameToMove = lbProject.SelectedIndex + _frameStart;
            if ((frameToMove - 1) < _frameStart)
            {
                return;
            }

            // Does this frame exist?
            int i = _frameList.FindIndex(c => c.frameNum == frameToMove);

            if (i >= 0)
            { 
                // Does the frame before this exist?
                int j = _frameList.FindIndex(c => c.frameNum == (frameToMove - 1));
                if (j >= 0)
                {
                    _frameList.RemoveAt(j); // Remove the old frame.
                    i = _frameList.FindIndex(c => c.frameNum == frameToMove); // Now that we removed the old frame, our i variable may have changed.
                }

                frameInfo fi = new frameInfo();
                fi.frameNum = (frameToMove - 1);
                fi.fileName = _frameList[i].fileName;
                _frameList[i] = fi;

                lbProject.SetSelected(lbProject.SelectedIndex - 1, true);
                MarkProjectDirty();
                RefreshList();
            }
            else
            {
                // We're on an in-between frame, so do nothing
            }
        }

        private void projectPropertiesToolStripMenuItem_Click(object sender, EventArgs e)
        {
            ShowProjectProperties();
        }

        private void ShowProjectProperties()
        {
            int origFrameStart = _frameStart;
            int origFrameEnd = _frameEnd;
            string origSourceDir = _sourceDir;
            string origOutputDir = _outputDir;
            string origOutputFilenameRoot = _outputFilenameRoot;

            frmProjectProperties pp = new frmProjectProperties();
            pp.frameStart = _frameStart;
            pp.frameEnd = _frameEnd;
            pp.sourceDir = _sourceDir;
            pp.outputDir = _outputDir;
            pp.outputFilenameRoot = _outputFilenameRoot;
            pp.projectDirectory = Path.GetDirectoryName(_projectFilename);
            if (pp.ShowDialog() == DialogResult.OK)
            {
                _frameStart = pp.frameStart;
                _frameEnd = pp.frameEnd;
                _sourceDir = pp.sourceDir;
                _outputDir = pp.outputDir;
                _outputFilenameRoot = pp.outputFilenameRoot;

                if (!Directory.Exists(_sourceDir))
                {
                    try
                    {
                        Directory.CreateDirectory(_sourceDir);
                    }
                    catch
                    {
                        // If we can't create it, oh well
                    }
                }

                if (!Directory.Exists(_outputDir))
                {
                    try
                    {
                        Directory.CreateDirectory(_outputDir);
                    }
                    catch
                    {
                        // If we can't create it, oh well
                    }
                }
                if ((origFrameStart != _frameStart) ||
                   (origFrameEnd != _frameEnd) ||
                   (origSourceDir != _sourceDir) ||
                   (origOutputDir != _outputDir) ||
                   (origOutputFilenameRoot != _outputFilenameRoot))
                {
                    MarkProjectDirty();
                }

                if ((origFrameStart != _frameStart) ||
                    (origFrameEnd != _frameEnd))
                {
                    RemoveFramesOutsideOfRange();
                    RefreshList();
                }
            }

            lbProject.Focus();
        }

        private void RemoveFramesOutsideOfRange()
        {
            for(int i=_frameList.Count - 1; i > -1; i--)
            {
                if ((_frameList[i].frameNum < _frameStart) ||
                    (_frameList[i].frameNum > _frameEnd))
                {
                    _frameList.RemoveAt(i);
                }
            }
        }

        private void MarkProjectDirty()
        {
            _projectDirty = true;
            this.Text = GetApplicationTitleBar() + " *";
        }

        private void MarkProjectClean()
        {
            _projectDirty = false;
            this.Text = GetApplicationTitleBar();
        }

        private string GetApplicationTitleBar()
        {
            string title;
            title = "BISE";

            if (_projectFilename.Trim().Length > 0)
            {
                title += " - [" + _projectFilename + "]";
            }

            return title;
        }

        private void frmMain_FormClosing(object sender, FormClosingEventArgs e)
        {
            if (_projectDirty)
            {
                DialogResult result = MessageBox.Show(@"""" + _projectFilename + @""" has changed. Do you want to save changes?",
                    "Save Changes?",
                    MessageBoxButtons.YesNoCancel,
                    MessageBoxIcon.Exclamation);
                if (result == DialogResult.Yes)
                {
                    SaveProject();
                }
                else if (result == DialogResult.Cancel)
                {
                    // Stop the closing and return to the form
                    e.Cancel = true;
                }
                else
                {
                    // Let it close
                    SaveProjectDefaults();
                }
            }

            mruMenu.SaveToRegistry();
        }

        private bool OpenProject()
        {
            bool retVal = false;
            toolStripStatusLabel1.Text = "Opening...";
            Application.DoEvents();

            string line = null;
            _frameList.Clear();

            try
            {
                using (System.IO.TextReader readFile = new StreamReader(_projectFilename))
                {
                    _frameStart = Convert.ToInt32(readFile.ReadLine());
                    _frameEnd = Convert.ToInt32(readFile.ReadLine());
                    _sourceDir = readFile.ReadLine();
                    _outputDir = readFile.ReadLine();
                    _outputFilenameRoot = readFile.ReadLine();
                    line = readFile.ReadLine(); // Reserved for future use
                    line = readFile.ReadLine(); // Reserved for future use
                    line = readFile.ReadLine(); // Reserved for future use
                    line = readFile.ReadLine(); // Reserved for future use
                    line = readFile.ReadLine(); // Reserved for future use
                    line = readFile.ReadLine(); // Reserved for future use
                    line = readFile.ReadLine(); // Reserved for future use
                    line = readFile.ReadLine(); // Reserved for future use
                    line = readFile.ReadLine(); // Reserved for future use
                    line = readFile.ReadLine(); // Reserved for future use
                    while (true)
                    {
                        line = readFile.ReadLine();
                        if (line != null)
                        {
                            frameInfo fi = new frameInfo();
                            fi.frameNum = Convert.ToInt32(line.Substring(0, (line.IndexOf("\t"))));
                            fi.fileName = line.Substring(line.IndexOf("\t") + 1);
                            _frameList.Add(fi);
                        }
                        else
                        {
                            break;
                        }
                    }
                }

                curFileName = _projectFilename;
                mruMenu.AddFile(curFileName);
                retVal = true;
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }

            MarkProjectClean();
            RefreshList();
            toolStripStatusLabel1.Text = "Ready";
            return retVal;
        }


        private void SaveProject()
        {
            toolStripStatusLabel1.Text = "Saving " + _projectFilename;
            Application.DoEvents();

            StringBuilder sb = new StringBuilder();
            sb.AppendLine(_frameStart.ToString());
            sb.AppendLine(_frameEnd.ToString());
            sb.AppendLine(_sourceDir);
            sb.AppendLine(_outputDir);
            sb.AppendLine(_outputFilenameRoot);
            sb.AppendLine(""); // reserved For future parameter
            sb.AppendLine(""); // reserved For future parameter
            sb.AppendLine(""); // reserved For future parameter
            sb.AppendLine(""); // reserved For future parameter
            sb.AppendLine(""); // reserved For future parameter
            sb.AppendLine(""); // reserved For future parameter
            sb.AppendLine(""); // reserved For future parameter
            sb.AppendLine(""); // reserved For future parameter
            sb.AppendLine(""); // reserved For future parameter
            sb.AppendLine(""); // reserved For future parameter

			for (int i = 0; i < _frameList.Count; i++)
            {
                sb.AppendLine(_frameList[i].frameNum.ToString() + "\t" + _frameList[i].fileName);
            }

            WriteFile(_projectFilename, sb.ToString());
            mruMenu.AddFile(_projectFilename);
            curFileName = _projectFilename;
            MarkProjectClean();
            toolStripStatusLabel1.Text = "Ready";

        }

        void WriteFile(string strFilePath, string strFileContents)
        {
            try
            {
                using (TextWriter writer = File.CreateText(strFilePath))
                {
                    writer.Write(strFileContents);
                }
            }
            catch (IOException ex)
            {
                Console.WriteLine(ex.ToString());
            }
        }

        private void saveProjectAsToolStripMenuItem_Click(object sender, EventArgs e)
        {
            SaveAs();
        }

        private bool SaveAs()
        {
            SaveFileDialog sdlg = new SaveFileDialog();
            if (File.Exists(_projectFilename))
            {
                sdlg.InitialDirectory = Path.GetDirectoryName(_projectFilename);
            }
            else if (File.Exists(_projectDirectory))
            {
                sdlg.InitialDirectory = Path.GetDirectoryName(_projectDirectory);
            }
 
            sdlg.AddExtension = true;
            sdlg.CheckPathExists = true;
            sdlg.CreatePrompt = false;
            sdlg.OverwritePrompt = true;
            sdlg.ValidateNames = true;
            sdlg.ShowHelp = true;
            sdlg.Filter = "BISE Files (*.bise)|*.bise";
            sdlg.DefaultExt = "bise";
            sdlg.FileName = _projectFilename;

            if (sdlg.ShowDialog() == DialogResult.OK)
            {
                _projectFilename = sdlg.FileName.ToString();
                SaveProject();
                return true;
            }
            else
            {
                return false;
            }
        }

        private void openProjectToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (_projectDirty)
            {
                DialogResult result = MessageBox.Show(@"""" + _projectFilename + @""" has changed. Do you want to save changes?",
                    "Save Changes?",
                    MessageBoxButtons.YesNoCancel,
                    MessageBoxIcon.Exclamation);
                if (result == DialogResult.Yes)
                {
                    SaveProject();
                }
                else if (result == DialogResult.Cancel)
                {
                    // Stop the closing and return to the form
                    return;
                }
                else
                {
                    // Let it close
                }
            }

            OpenFileDialog sourceFileOpenFileDialog = new OpenFileDialog();

            if (_projectFilename.Trim().Length > 0)
            {
                sourceFileOpenFileDialog.InitialDirectory = Path.Combine(Path.GetDirectoryName(_projectFilename), _sourceDir);
            }

            sourceFileOpenFileDialog.Filter = "BISE Files (*.bise)|*.bise";
            sourceFileOpenFileDialog.RestoreDirectory = true;
            sourceFileOpenFileDialog.Multiselect = false;
            sourceFileOpenFileDialog.Title = "Please select BISE project file";

            if (sourceFileOpenFileDialog.ShowDialog() == DialogResult.OK)
            {
                _projectFilename = sourceFileOpenFileDialog.FileName;
                OpenProject();
            }            
        }

        private void newProjectToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (_projectDirty)
            {
                DialogResult result = MessageBox.Show(@"""" + _projectFilename + @""" has changed. Do you want to save changes?",
                    "Save Changes?",
                    MessageBoxButtons.YesNoCancel,
                    MessageBoxIcon.Exclamation);
                if (result == DialogResult.Yes)
                {
                    SaveProject();
                }
                else if (result == DialogResult.Cancel)
                {
                    // Stop the closing and return to the form
                    return;
                }
                else
                {
                    // Let it close
                }
            }

            LoadNewProjectDefaults();
            RefreshList();
            MarkProjectClean();
            if (SaveAs())
            {
                // Come up with our output filename root based on the directory name.
                string[] directories = _projectFilename.Split(Path.DirectorySeparatorChar);
                if ((directories.Count() - 2) > 0)
                {
                    _outputFilenameRoot = directories[directories.Count() - 2];
                }

                ShowProjectProperties();
                RefreshList();
            }
        }

        private void LoadNewProjectDefaults()
        {
            _frameList.Clear();
            RegistryKey regBISE = Registry.CurrentUser.CreateSubKey(@"Software\JBCustom\BISE");
            _frameStart = Convert.ToInt32(regBISE.GetValue("_frameStart", (object)1));
            _frameEnd = Convert.ToInt32(regBISE.GetValue("_frameEnd", (object)500));
            _multiRate = Convert.ToInt32(regBISE.GetValue("_multiRate", (object)1));
            _sourceDir = Convert.ToString(regBISE.GetValue("_sourceDir", (object) ""));
            _outputDir = Convert.ToString(regBISE.GetValue("_outputDir", (object)""));
            _outputFilenameRoot = Convert.ToString(regBISE.GetValue("_outputFilenameRoot", (object)"output"));
            _projectDirectory = Convert.ToString(regBISE.GetValue("_projectDirectory", (object)""));
            _projectFilename = "";
        }


        private void SaveProjectDefaults()
        {
            RegistryKey regBISE = Registry.CurrentUser.CreateSubKey(@"Software\JBCustom\BISE");
            regBISE.SetValue("_frameStart", _frameStart);
            regBISE.SetValue("_frameEnd", _frameEnd);
            regBISE.SetValue("_multiRate", _multiRate);
            regBISE.SetValue("_sourceDir", _sourceDir);
            regBISE.SetValue("_outputDir", _outputDir);
            regBISE.SetValue("_outputFilenameRoot", _outputFilenameRoot);
            regBISE.SetValue("_projectDirectory", Path.GetDirectoryName(_projectFilename));
        }

        private void frmMain_DragEnter(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop)) e.Effect = DragDropEffects.Copy;
        }

        private void frmMain_DragDrop(object sender, DragEventArgs e)
        {
            string fileToLoad = "";
            string[] files = (string[])e.Data.GetData(DataFormats.FileDrop);
            if (files.Length > 0)
            {
                fileToLoad = files[0];

                if (_projectDirty)
                {
                    DialogResult result = MessageBox.Show(@"""" + _projectFilename + @""" has changed. Do you want to save changes?",
                        "Save Changes?",
                        MessageBoxButtons.YesNoCancel,
                        MessageBoxIcon.Exclamation);
                    if (result == DialogResult.Yes)
                    {
                        SaveProject();
                    }
                    else if (result == DialogResult.Cancel)
                    {
                        // Stop the closing and return to the form
                        return;
                    }
                    else
                    {
                        // Let it close
                    }
                }

                _projectFilename = fileToLoad;
                OpenProject();
            }
        }

        private void bakeSourceAlphaFilesToolStripMenuItem_Click(object sender, EventArgs e)
        {
            toolStripProgressBar1.Visible = true;
            toolStripProgressBar1.Minimum = _frameStart;
            toolStripProgressBar1.Maximum = _frameEnd;

            // Make our source "alpha" directory if it doesn't exist.
            if (!Directory.Exists(Path.Combine(Path.GetDirectoryName(_projectFilename), _sourceDir) + @"\alpha"))
            {
                Directory.CreateDirectory(Path.Combine(Path.GetDirectoryName(_projectFilename), _sourceDir) + @"\alpha");
            }

            for (int i = _frameStart; i <= _frameEnd; i++)
            {
                toolStripProgressBar1.Value = i;
                frameInfo item = _frameList.Find(c => c.frameNum == i);
                toolStripStatusLabel1.Text = "Baking " + item.fileName;
                Application.DoEvents();
                if ((item.frameNum == i) && (item.fileName != null))
                {
                    if (!DoesFileHaveSourceAlpha(item.fileName))
                    {
                        BakeSourceAlpha(item.fileName);
                    }
                } 
            }

            toolStripStatusLabel1.Text = "Ready";
            MessageBox.Show("Baked images to " + Path.Combine(Path.GetDirectoryName(_projectFilename), _sourceDir) + @"\alpha\", "Done!");
            toolStripProgressBar1.Value = _frameStart;
            toolStripProgressBar1.Visible = false;
        }

        private bool DoesFileHaveSourceAlpha(string fileName)
        {
            if (File.Exists(Path.Combine(Path.GetDirectoryName(_projectFilename), _sourceDir) + @"\alpha\" + fileName))
            {
                return true;
            }
            else
            {
                return false;
            }
        }


        private void BakeSourceAlpha(string fileName)
        {
            // We only make mask images for images that don't exist. We don't check for "correctness"
            // Now write the mask image based on the alpha channel.
            Bitmap image = (Bitmap)Image.FromFile(Path.Combine(Path.GetDirectoryName(_projectFilename), _sourceDir) + @"\" + fileName);

            //Get the bitmap data
            var bitmapData = image.LockBits(
                new Rectangle(0, 0, image.Width, image.Height),
                ImageLockMode.ReadWrite,
                image.PixelFormat
            );

            //Initialize an array for all the image data
            byte[] imageBytes = new byte[bitmapData.Stride * image.Height];

            //Copy the bitmap data to the local array
            Marshal.Copy(bitmapData.Scan0, imageBytes, 0, imageBytes.Length);

            //Unlock the bitmap
            image.UnlockBits(bitmapData);

            //Find pixelsize
            int pixelSize = Image.GetPixelFormatSize(image.PixelFormat);

            // An example on how to use the pixels, lets make a copy
            int x = 0;
            int y = 0;
            var bitmap = new Bitmap(image.Width, image.Height);

            //Loop pixels
            int channelsToCopy = pixelSize / 8;
            for (int j = 0; j < imageBytes.Length; j += channelsToCopy)
            {
                //Copy the bits into a local array
                var pixelData = new byte[4];
                Array.Copy(imageBytes, j, pixelData, 0, channelsToCopy);

                if (channelsToCopy == 4)
                {
                    // We have an alpha channel.
                    //Get the color of a pixel
                    var color = Color.FromArgb(pixelData[3], pixelData[0], pixelData[1], pixelData[2]);

                    //Set the color of a pixel
                    bitmap.SetPixel(x, y, Color.FromArgb(255, 255 - color.A, 255 - color.A, 255 - color.A));
                }
                else // channelsToCopy == 3
                {
                    // There is no alpha channel. Go pure black.
                    bitmap.SetPixel(x, y, Color.Black);
                }

                //Map the 1D array to (x,y)
                x++;
                if (x >= image.Width)
                {
                    x = 0;
                    y++;
                    if (y >= image.Height)
                    {
                        // I'm not sure how this can happen, but I've seen it with a 711x396 image with no alpha channel. When you do the
                        // math, it turns out that you have a height of 396.5569620253165 pixels. Not sure how that extra half pixel value 
                        // ends up in there, but it's possible. So get out of here.
                        break;
                    }
                }
            }

            // Bake the local alpha
            bitmap.Save(Path.Combine(Path.GetDirectoryName(_projectFilename), _sourceDir) + @"\alpha\" + fileName);
        }

        private void deleteImageandShiftLaterImagesBackToolStripMenuItem_Click(object sender, EventArgs e)
        {
            int deleteFrameNum = lbProject.SelectedIndex + _frameStart;
            ClearFrame(deleteFrameNum);
            
            var indexes = _frameList.Select((c, index) => c.frameNum > deleteFrameNum ? index : -1).Where(i => i >= 0).ToArray();
            for (int i = 0; i<indexes.Length; i++)
            {
                frameInfo fi = _frameList[indexes[i]];
                fi.frameNum--;
                _frameList[indexes[i]] = fi;
            }

            MarkProjectDirty();
            RefreshList();
        }

        private void mnuAboutBISE_Click(object sender, EventArgs e)
        {
            frmAbout About = new frmAbout();
            About.ShowDialog();
        }

        private void insertFrameToolStripMenuItem_Click(object sender, EventArgs e)
        {
            int insertFrameNum = lbProject.SelectedIndex + _frameStart - 1;

            var indexes = _frameList.Select((c, index) => c.frameNum > insertFrameNum ? index : -1).Where(i => i >= 0).ToArray();
            for (int i = 0; i < indexes.Length; i++)
            {
                frameInfo fi = _frameList[indexes[i]];
                fi.frameNum++;
                _frameList[indexes[i]] = fi;
            }

            MarkProjectDirty();
            RefreshList();
        }

        private void OnMruFile(int number, String filename)
        {
            if (_projectDirty)
            {
                DialogResult result = MessageBox.Show(@"""" + _projectFilename + @""" has changed. Do you want to save changes?",
                    "Save Changes?",
                    MessageBoxButtons.YesNoCancel,
                    MessageBoxIcon.Exclamation);
                if (result == DialogResult.Yes)
                {
                    SaveProject();
                }
                else if (result == DialogResult.Cancel)
                {
                    // Stop the closing and return to the form
                    return;
                }
                else
                {
                    // Let it close
                }
            }

            _projectFilename = filename;
            if (OpenProject())
            {
                mruMenu.SetFirstFile(number);
            }
            else
            {
                mruMenu.RemoveFile(number);
            }
        }

        private void IncFilename()
        {
            m_curFileNum++;
        }
    }
}
