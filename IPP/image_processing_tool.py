2#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import glob
import os.path
import csv
import threading
import time
from StringIO import StringIO


import wx
import xml.etree.ElementTree as ET
import process_max_gui

from aux_gui import *
import pm
import Image
import shutil
working_folder = os.curdir
############################################################################
############################################################################
############################################################################
processed_image_count = 0
image_process_limit = 10000 #limit number of images to be processed at a time

def process_xml(filename):
    global processed_image_count
    if processed_image_count < image_process_limit:
        root = ET.parse(filename).getroot()
        fepid = root[0].text
        number = root[1].text
        imagevr = pm.facedetect(root[2].text)
        face_count = len(imagevr)
        if face_count == 1:
            """
            if only 1 face detected in image face will be cropped and put the image in 
            cropped folder while the original image and xml will go in processed folder.
            """
            detect = 1
            reason = str(imagevr)
            image_path = working_folder+"/processed/" +fepid+".jpg"
            xml_file_path = working_folder+"/processed/"+filename.split('\\')[-1]
            fh = open(image_path, "wb")
            fh.write(root[2].text.decode('base64'))
            fh.close()
            crop_image_open = Image.open(image_path)
            output_img = crop_image_open.crop(((imagevr[0][0]-13,
                                                 imagevr[0][1]-33, 
                                                 imagevr[0][2]+imagevr[0][0]+20, 
                                                 imagevr[0][3]+imagevr[0][1]+50)))
            output_img.save(working_folder+"/cropped/" +fepid+".jpg")
            shutil.copy2(filename, xml_file_path)
        else:
            detect = 0
            if face_count < 1:
                """
                if more than 1 face detected in image, the original image and xml will go in reject folder.
                """
                image_path = working_folder+"/reject/" +fepid+".jpg"
                xml_file_path = working_folder+"/reject/" +filename.split('\\')[-1]
                fh = open(image_path, "wb")
                fh.write(root[2].text.decode('base64'))
                fh.close()
                shutil.copy2(filename, xml_file_path)
                reason = "No face detected"
            else:
                """
                if no face detected in image, the original image and xml will go in reject folder.
                """
                image_path = working_folder+"/reject/" +fepid+".jpg"
                xml_file_path = working_folder+"/reject/" +filename.split('\\')[-1]
                fh = open(image_path, "wb")
                fh.write(root[2].text.decode('base64'))
                fh.close()
                shutil.copy2(filename, xml_file_path)
                reason = str(face_count) + " faces detected"
                    
        image_dump = pm.decode_image(root[2].text)
        image = StringIO()
        image.write(image_dump)
        image.seek(0)
        processed_image_count += 1
#        print processed_image_count
        return [ 'Someone', str(fepid), str(number), str(detect), str(reason), image]
    else:
        return None

############################################################################
############################################################################
############################################################################

XML_FILENAMES = None
STOP = False
TIME_REMAINING = 'You must calculate it!'
TIME_ELAPSED = 0

# Thread class that executes processing
class WorkerThread(threading.Thread):
    def __init__(self, parent, value):
        """
        @param parent: The gui object that should recieve the value
        @param value: value to 'calculate' to
        """
        threading.Thread.__init__(self)
        self._parent = parent
        self._value = value
        self.processed = None
        self.gauge = 0

    def run(self):
        """
        Overrides Thread.run. Don't call this directly its called internally
        when you call Thread.start().
        """
        global PROCESSED
        global STOP
        global TIME_REMAINING
        global TIME_ELAPSED

        how_much_files = total_files = len(XML_FILENAMES)

        for f in XML_FILENAMES:
            if STOP: return
            how_much_files -= 1

            start = time.time()
            time.sleep(0.3)            
            self.processed = process_xml(f)
            end = time.time()

            TIME_ELAPSED += (end - start)
            TIME_REMAINING = '%.2f seconds' % \
                (((TIME_ELAPSED)/(total_files-how_much_files))*how_much_files)

            # Twice, before the screen update 
            if STOP: return

            wx.CallAfter(self.doit)
        
        self._parent.button_download.Enable()
        self._parent.button_process_xml_batch.Enable()


    def doit(self):
        self._parent.processed.append(self.processed)
        self.gauge += 1
        self._parent.gauge_completion.SetValue(self.gauge)

        # Append the processed information on a list, excluding the path for the image
        self._parent.insert_info_list_batch(self.processed)

        # Display the time remaining
        self._parent.label_time_remaining.SetLabel('Time Remaining: %s' % TIME_REMAINING)

        self._parent.Update()

# Thread class that executes processing single
class WorkerThreadSingle(threading.Thread):
    def __init__(self, parent, value, xml_file):
        """
        @param parent: The gui object that should recieve the value
        @param value: value to 'calculate' to
        """
        threading.Thread.__init__(self)
        self._parent = parent
        self._value = value
        self.xml_file = xml_file
        self.processed = None
        self.gauge = 0

    def run(self):
        """
        Overrides Thread.run. Don't call this directly its called internally
        when you call Thread.start().
        """

        wx.CallAfter(self.doit)
        
    def doit(self):
        self.processed = process_xml(self.xml_file)
        self._parent.display_subscriber(self.processed)

        # Append the processed information on a list, excluding the path for the image
        self._parent.insert_info_list_batch(self.processed)

        # Display the time remaining
        self._parent.label_time_remaining.SetLabel('Time Remaining: %s' % TIME_REMAINING)

        self._parent.Update()

class MainFrame(process_max_gui.MainFrame):
    def __init__(self, *args, **kwds):
        process_max_gui.MainFrame.__init__(self, *args, **kwds)

        # After the XML files are decoded, they will be here, to be displayed
        # The information to be displayef will be here.
        self.origdir = os.getcwd()

        self.xml_filenames = []
        
        self.max_file_batch = 0

        self.processed = []

        self.current_single_xml = ''

        # Binds Buttons with functions
        self.set_binds()

        self.init_list_crtl_subscriber()
        self.init_list_crtl_xml_files()

    def set_binds(self):
        self.Bind(wx.EVT_BUTTON, self.select_folder_single, self.button_select_folder_single)
        self.Bind(wx.EVT_BUTTON, self.select_folder_batch, self.button_select_folder_batch)
        self.Bind(wx.EVT_BUTTON, self.select_file, self.button_select_file)
        self.Bind(wx.EVT_BUTTON, self.process_files_batch, self.button_process_xml_batch)
        self.Bind(wx.EVT_BUTTON, self.process_files_single, self.button_process_xml_single)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.item_selected, self.list_ctrl_xml_files)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.select_subscriber, self.list_ctrl_subscriber)
        self.Bind(wx.EVT_BUTTON, self.download_data, self.button_download)
        self.Bind(wx.EVT_BUTTON, self.stop_thread, self.button_cancel)
        self.Bind(wx.EVT_BUTTON, self.clear_all, self.button_clear_all_single)
        self.Bind(wx.EVT_BUTTON, self.clear_all, self.button_clear_all_batch)

    def item_selected(self, event):
        num = self.list_ctrl_xml_files.GetFocusedItem()
        name = self.xml_filenames[num]
        self.current_single_xml = name

        # Writes the filename in the file dialog
        self.text_ctrl_xml_file.SetValue(os.path.basename(name))

        # Enable the processing button
        #self.button_process_xml_single.Enable()

        # Processes the file
        w = WorkerThreadSingle(self, 1, self.current_single_xml)
        w.start()

        # Updates the GUI
        self.Refresh()

    def select_folder_single(self, event):
        
        # Get the path
        folder = get_path(self)

        if not folder: return None
        # Update the folder path
        self.text_ctrl_xml_folder2.SetValue(os.path.basename(folder))

        # Reads the xml files that are on the folder
        self.xml_filenames = glob.glob(folder + '/*.xml') 

        # Shows in the XML list the files
        for f in self.xml_filenames:
            name = os.path.basename(f)

            self.insert_info_list_single(name)

    def select_folder_batch(self, event):
        # Get the path
        folder = get_path(self)

        if not folder: return None

        # Update the folder path
        self.text_ctrl_xml_folder1.SetValue(os.path.basename(folder))


        # Reads the xml files that are on the folder
        self.xml_filenames = glob.glob(folder + '/*.xml') 

        # Set the gauge range to match the amount of files in the folder
        self.max_file_batch = len(self.xml_filenames)
        #self.max_file_batch = 5 # Delete this line after you've coded the xml coder
        self.init_gauge(self.max_file_batch)

        # Enable the processing button
        self.button_process_xml_batch.Enable()


    def select_file(self, event):
        xml_file = open_file_diag(self, '.', wildcard='XML files (*.xml)|*.xml')
        if not xml_file: return None
        self.current_single_xml = xml_file
        self.text_ctrl_xml_file.SetValue(os.path.basename(xml_file))

        # Enable the processing button
        self.button_process_xml_single.Enable()

    
    def download_data(self, event):
        filename = save_file_diag(self, 'data.csv', '.', wildcard='CSV files (*.csv)|*.csv')
        if not filename: return None

        f = open(filename, 'wb')

        if self.combo_box_download.GetSelection() == 0: # CSV
            writer = csv.writer(f)
        else: # Excel
            # This part can be redesigned to use a more robust Excel backend
            writer = csv.writer(f, dialect='excel')
            
        for p in self.processed:
            writer.writerow(p[:-1])

    def process_files_batch(self, event):
        global TIME_ELAPSED
        TIME_ELAPSED = 0


        # Make the STOP False, in case someone pressed cancel earlier
        global STOP
        STOP = False

        global XML_FILENAMES
        XML_FILENAMES = self.xml_filenames

        # Disable the batch processing button
        self.button_process_xml_batch.Disable()

        w = WorkerThread(self, 1)
        w.start()

    def process_files_single(self, event):
        processed = process_xml(self.current_single_xml)
        self.display_subscriber(processed)


    def display_subscriber(self, processed):
        self.text_ctrl_subscriber_name.SetValue(processed[0])
        self.text_ctrl_uid.SetValue(processed[1])
        self.text_ctrl_phone.SetValue(processed[2])
        self.text_ctrl_image_verif.SetValue(processed[3])
        self.text_ctrl_reason.SetValue(processed[4])

        if processed[5]:
            image = wx.ImageFromStream(processed[5], wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            self.bitmap_subscriber.SetBitmap(image)
        self.Refresh()
        self.Layout()

    def select_subscriber(self, event):
        lista = self.list_ctrl_subscriber
        num = lista.GetFocusedItem()

        item = self.processed[num]
        # #index = lista.InsertStringItem(sys.maxint, xml_file)
        # for i in xrange(lista.GetItemCount()):
        #     t = []
        #     for j in xrange(lista.GetColumnCount()):
        #         t.append(lista.GetItem(i, j).GetText())
        # t.append(None) # You must change this to the image that should be displayed

        self.display_subscriber(item)
        self.notebook_xml.SetSelection(1)
        
    def insert_info_list_batch(self, subscriber):
        try:
            lista = self.list_ctrl_subscriber
            index = lista.InsertStringItem(sys.maxint, subscriber[0])
            lista.SetStringItem(index, 1, subscriber[1])
            lista.SetStringItem(index, 2, subscriber[2])
            lista.SetStringItem(index, 3, subscriber[3])
            lista.SetStringItem(index, 4, subscriber[4])
        except:
            pass

    def insert_info_list_single(self, xml_file):
        lista = self.list_ctrl_xml_files
        index = lista.InsertStringItem(sys.maxint, xml_file)


    def init_list_crtl_subscriber(self):
        lista = self.list_ctrl_subscriber
        lista.InsertColumn(0, 'Subscriber')
        lista.InsertColumn(1, 'UID')
        lista.InsertColumn(2, 'Phone Number')
        lista.InsertColumn(3, 'Detect')
        lista.InsertColumn(4, 'Reason')
        lista.SetColumnWidth(0, 250)
        lista.SetColumnWidth(2, 150)

    def init_list_crtl_xml_files(self):
        lista = self.list_ctrl_xml_files
        lista.InsertColumn(0, 'XML Files')
        lista.SetColumnWidth(0, 250)

    def clear_all(self, event):
        global TIME_ELAPSED
        TIME_ELAPSED = 0

        self.processed = []
        self.gauge_completion.SetValue(0)

        #self.list_ctrl_subscriber.ClearAll()
        num = self.list_ctrl_subscriber.GetItemCount()
        for i in xrange(num):
            self.list_ctrl_subscriber.DeleteItem(0)

        #self.list_ctrl_xml_files.ClearAll()
        num = self.list_ctrl_xml_files.GetItemCount()
        for i in xrange(num):
            self.list_ctrl_xml_files.DeleteItem(0)

        self.bitmap_subscriber.SetBitmap(wx.Bitmap(self.origdir + '/Untitled.png'))


        self.text_ctrl_xml_folder1.Clear()
        self.text_ctrl_xml_folder2.Clear()

        self.text_ctrl_image_verif.Clear()
        self.text_ctrl_phone.Clear()
        self.text_ctrl_reason.Clear()
        self.text_ctrl_subscriber_name.Clear()
        self.text_ctrl_uid.Clear()
        self.text_ctrl_xml_file.Clear()

        self.button_process_xml_batch.Disable()
        self.button_process_xml_single.Disable()
        self.button_download.Disable()

    # Define the range of the gauge
    def init_gauge(self, size=10):
        self.gauge_completion.SetRange(size)

    def stop_thread(self, event):
        global STOP
        if popup_message(self, 'Are you sure you want to cancel', 'Stop processing', wx.NO|wx.YES|wx.ICON_QUESTION):
            STOP = True
            
            # Enable the batch processing button
            self.button_process_xml_batch.Enable()
            
            # Enable the download button
            self.button_download.Enable()

if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_main = MainFrame(None, -1, "")
    app.SetTopWindow(frame_main)
    frame_main.Show()
    app.MainLoop()
