from tkinter import *
from tkinter import messagebox
import validators # to check URL validity
import os # deprecated but works just fine
import webbrowser # for about page
from urllib.parse import urlparse # to parse YouTube URL data

# Initialize Window
version = "1.4"
root = Tk()
root.title('YT-DLP-GUI ' + version)
#root.iconbitmap('img/favicon.ico')
root.resizable(False, False)

# Callback Webpage
def callback(url):
    webbrowser.open_new(url)

# About Page
def open_about():
    top = Toplevel()
    top.title('About')
    #top.iconbitmap('img/favicon.ico')
    top.resizable(False, False)
    ver = Label(top, text="YT-DLP-GUI Version " + version)
    ver.config(font=("Segoe UI", 20))
    ver.pack(padx=10,pady=5)
    built = Label(top, text="Sunday, 25.09.2022")
    built.config(font=("Segoe UI",16))
    built.pack(padx=5)
    credit = Label(top, text="Developed by FlamingLeo, 2021 - 2022.")
    credit.config(font=("Segoe UI", 8))
    credit.pack(padx=5)
    Button(top, text="YT-DLP GitHub", command = lambda: callback("github.com/yt-dlp/yt-dlp"),padx=5,pady=5).pack(padx=5,pady=5)

# Update YT-DLP
def update():
    os.system('start cmd /c yt-dlp.exe -U')

# Frame for URL
url_frame = LabelFrame(root, text="URL",padx=10,pady=10)
url_frame.pack(expand=True, fill='both',padx=10,pady=10)

# Inputbox for YouTube URL
url = Entry(url_frame, width=45, borderwidth=2)
url.grid(row=0,column=0,sticky=W)

# Choose, whether to optimize link (yt standard) or not (all websites)
url_format = [
    "YouTube URL", # Choosing this option will parse the link to only include 11-character identifier to cancel downloading of entire playlists
    "General URL" # Parse whole URL
]

uf_chosen = StringVar()
uf_chosen.set(url_format[0])

uf = OptionMenu(url_frame, uf_chosen, *url_format)
uf.grid(row=0,column=1,padx=3, sticky=E)
uf.configure(width=14)

# Rightclick menu
def url_popup(e):
    url_menu.tk_popup(e.x_root, e.y_root)

# Inputbox Modification
def url_modify(value):
    if value == 0:
        url.insert(0, root.clipboard_get())
    elif value == 1:
        url.delete(0, 'end')
        url.insert(0, root.clipboard_get())
    elif value == 2:
        url.delete(0, 'end')
        url.insert(0, root.clipboard_get())
        add_to_listbox()
    elif value == 3:
        url.delete(0, 'end')
        url.insert(0, root.clipboard_get())
        download()
    else:
        url.delete(0, 'end')

# Inputbox rightclick menu
url_menu = Menu(root,tearoff=False)
url_menu.add_command(label="Paste", command=lambda:url_modify(0))
url_menu.add_command(label="Replace", command=lambda:url_modify(1))
url_menu.add_command(label="Replace and add to queue", command=lambda:url_modify(2))
url_menu.add_command(label="Replace and download", command=lambda:url_modify(3))
url_menu.add_command(label="Clear", command=lambda:url_modify(4))

url.bind("<Button-3>", url_popup)

# Create argument list
args_list = []

# Create frame for dropdown & radio buttons
settings = LabelFrame(root, text="Download Settings",padx=10,pady=10)
settings.pack(expand=True, fill='both',padx=10,pady=10)

# Variables and lists for radio button & dropdowns
video_format = [ # --remux-video, unless default
    "default",
    "webm",
    "mov",
    "avi",
    "mp3",
    "mka",
    "m4a",
    "ogg",
    "opus"
]

vf_chosen = StringVar() # chosen dropdown option
vf_chosen.set(video_format[0]) # sets default option to first in list

audio_format = [ # --audio-format, unless default
    "default",
    "opus",
    "aac",
    "flac",
    "mp3",
    "m4a",
    "vorbis",
    "wav"
]

af_chosen = StringVar() # chosen dropdown option
af_chosen.set(audio_format[0]) # sets default option to first in list

dl = IntVar() # chosen radio button
dl.set('1') # sets first default radio button as active

vf = OptionMenu(settings, vf_chosen, *video_format)
vf.configure(width=7)
af = OptionMenu(settings, af_chosen, *audio_format)
af.configure(width=7,state="disabled") # default, since first option is video + audio

chosen_format = ""

# Disable certain dropdown based on radiobutton choice
def choice():
    global chosen_format
    if dl.get() == 1:
        if chosen_format in args_list:
            args_list.remove(chosen_format)
        vf.configure(state="normal")
        af.configure(state="disabled")
        if vf_chosen.get() != "default":
            chosen_format = "--remux-video " + vf_chosen.get()
            if chosen_format not in args_list:
                args_list.append(chosen_format)
        #print(args_list)
    elif dl.get() == 2:
        if chosen_format in args_list:
            args_list.remove(chosen_format)
        vf.configure(state = "disabled")
        af.configure(state="normal")
        if af_chosen.get() != "default":
            chosen_format = "--extract-audio --audio-format " + af_chosen.get()
            if chosen_format not in args_list:
                args_list.append(chosen_format)
        else:
             chosen_format = "--extract-audio"
             if chosen_format not in args_list:
                args_list.append(chosen_format)
        #print(args_list)


# Radio buttons: Choose between video + audio or just audio
Radiobutton(settings, text = "Video + Audio                      ", variable = dl, value = 1, command=choice).grid(row=0,column=0,sticky=W) #shithouse method of adding spaces
Radiobutton(settings, text = "Audio Only", variable = dl, value = 2, command=choice).grid(row=1,column=0,sticky=W)

# Dropdowns: Select video / audio formats
vf.grid(row=0,column=1,padx=5)
af.grid(row=1, column=1,padx=5)

# Check boxes: Choose extra features

# Advanced options and About page
advanced = Button(settings, text="Advanced Settings", state=DISABLED, padx=10)
advanced.configure(width=15)
advanced.grid(row=0,column=2,padx=5)
about = Button(settings, text="Update YT-DLP-GUI", command=update, padx=10)
about.configure(width=15)
about.grid(row=1,column=2,padx=5)

# Listbox frame for Scrollbar
listbox_frame = Frame(root)
listbox_scrollbar = Scrollbar(listbox_frame, orient=VERTICAL)

# URL Listbox
url_list = []
url_listbox = Listbox(listbox_frame,width=67,borderwidth=2, yscrollcommand= listbox_scrollbar.set,selectmode=MULTIPLE)
listbox_scrollbar.config(command=url_listbox.yview)
listbox_scrollbar.pack(side=RIGHT,fill=Y)
listbox_frame.pack()
url_listbox.pack(padx=10)

# Check if URL is valid
def check_validity(link): #to be fixed
    global is_valid
    is_valid = 0
    if not validators.url(link):
        messagebox.showinfo('Invalid URL', 'Please enter a valid URL.')
    else:
        is_valid = 1

# Save URLs once in memory
saved_links = []

# Add to listbox function
def add_to_listbox():
    check_validity(url.get())
    if url.get() not in url_list and url.get() != '' and is_valid == 1:
        url_listbox.insert(END, url.get())
        url_list.append(url.get())
        saved_links.append(url.get())
        url.delete(0, END)

# Remove from listbox function
def remove_from_listbox():
    for item in reversed(url_listbox.curselection()):
        url_listbox.delete(item)
        url_list.remove(url_list[item])

# Clear listbox function
def clear_listbox():
    url_listbox.delete(0,END)
    url_list.clear()

# Restore listbox function
def restore_listbox():
    for link in saved_links:
        if link not in url_list:
            url_listbox.insert(END, link)
            url_list.append(link)

# Clear stored listbox entries
def clear_saved():
    saved_links.clear()

# Download function - Opens a cmd window: opens yt-dlp, introduces chosen args and URL
def download():
    choice() # reload choice to update file format. lame fix but It Just Works™
    # If Link Optimization is on
    if uf_chosen.get() == "YT Standard":
        for idx, link in enumerate(url_list):
            link = urlparse(url).query[2:13]
            url_list[idx] = link
    urls = ' '.join([str(item) for item in url_list])
    args = ' '.join([str(item) for item in args_list])
    if urls == '' and not url.get(): # If there is no URL in the input box and no URL in the listbox, the program will display an error message.
        messagebox.showinfo('Invalid URL', 'The URL box cannot be blank.')
    elif urls == '' and url.get() != '': # If there is a link in the input box but no URL in the listbox, the program will send the link in the input box to YT-DLP.
        check_validity(url.get())
        if is_valid == 1:
            # If Link Optimization is on
            if uf_chosen.get() == "YT Standard":
                url_cat = urlparse(url.get()).query[2:13]
                os.system('start cmd /c yt-dlp ' + args + " " + url_cat)
            else:
                os.system('start cmd /c yt-dlp ' + args + " " + url.get())
    else: # You figure it out.
        os.system('start cmd /c yt-dlp ' + args + " " + urls)
    clear_listbox()
    clear_saved()
    url.delete(0, 'end')

# Queue Options frame
queue = LabelFrame(root, text="Queue Settings",padx=10,pady=10)
queue.pack(expand=True, fill='both',padx=10,pady=10)

# Add to listbox button
add = Button(queue, text="Add", command=add_to_listbox, padx=5, pady=5)
add.pack(expand=True, fill='both', side='left',padx=5)

# Remove from listbox button
remove = Button(queue, text="Remove", command=remove_from_listbox, padx=5, pady=5)
remove.pack(expand=True, fill='both', side='left',padx=5)

# Clear listbox button
clear = Button(queue, text="Clear", command=clear_listbox, padx=5, pady=5)
clear.pack(expand=True, fill='both', side='left',padx=5)

# Restore listbox button
restore = Button(queue, text="Restore", command=restore_listbox, padx=5, pady=5)
restore.pack(expand=True, fill='both', side='left',padx=5)

# Download button
submit = Button(root, text="Download", command=download, padx=5, pady=5)
submit.pack(fill='x',padx=10,pady=10)


# Menu bar
root_menu = Menu(root)
root.config(menu=root_menu)

file_menu = Menu(root_menu,tearoff=0)
root_menu.add_cascade(label="URL", menu=file_menu)
file_menu.add_command(label="Paste", command=lambda:url_modify(0))
file_menu.add_command(label="Replace", command=lambda:url_modify(1))
file_menu.add_command(label="Replace and add to queue", command=lambda:url_modify(2))
file_menu.add_command(label="Replace and download", command=lambda:url_modify(3))
file_menu.add_command(label="Clear", command=lambda:url_modify(4))

queue_menu = Menu(root_menu,tearoff=0)
root_menu.add_cascade(label="Queue", menu=queue_menu)
queue_menu.add_command(label="Add URL from input field",command=add_to_listbox)
queue_menu.add_command(label="Add URL from clipboard",command=lambda:url_modify(2))
queue_menu.add_command(label="Clear",command=clear_listbox)
queue_menu.add_command(label="Restore",command=restore_listbox)
queue_menu.add_separator()
queue_menu.add_command(label="Download",command=download)

help_menu = Menu(root_menu,tearoff=0)
root_menu.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="About", command=open_about)
help_menu.add_command(label="Update YT-DLP", command=update)


root.mainloop()

"""
TODO:
- Add advanced options in another window/tab
- Add check to see if YT-DLP is in same folder
- Enable use of only identifiers
- Choose custom ytdlp location
- Choose download path
- List feature
- Add search feature
- Load links from file
"""