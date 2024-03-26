#!/usr/bin/env python3
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from urllib.parse import urlparse
import validators
import yt_dlp
import threading
import sys
import os
import pip


class Logger:
    def debug(self, msg): return log_if_option_chosen(log_info, msg)
    def warning(self, msg): return log_if_option_chosen(log_warn, msg)
    def error(self, msg): return log_if_option_chosen(log_err, msg)


# dropdown lists
FORMAT_NAMES = [
    "default",
    "best",
    "best*",
    "bestvideo",
    "bestvideo*",
    "bestaudio",
    "bestaudio*",
    "worst",
    "worst*",
    "worstvideo",
    "worstvideo*",
    "worstaudio",
    "worstaudio*"
]

FORMAT_FILETYPES = [
    "3gp",
    "aac",
    "flv",
    "m4a",
    "mp3",
    "mp4",
    "ogg",
    "wav",
    "webm"
]

AUDIO_FORMATS = [
    "aac",
    "alac",
    "flac",
    "m4a",
    "mp3",
    "opus",
    "vorbis",
    "wav"
]

REMUX_RECODE_FORMATS = [
    "avi",
    "flv",
    "gif",
    "mkv",
    "mov",
    "mp4",
    "webm",
    "aac",
    "aiff",
    "alac",
    "flac",
    "m4a",
    "mka",
    "mp3",
    "ogg",
    "opus",
    "vorbis",
    "wav"
]

FIXUP_POLICIES = [
    'never',
    'ignore',
    'warn',
    'detect_or_warn',
    'force'
]

VERSION = "2.2"
DATE = "26.03.2024"
DUMMY_VIDEO = "https://www.youtube.com/watch?v=Vhh_GeBPOhs"
CONCURRENT_LIMIT = 10

download_archive_path = ""
cookie_file_path = ""
certfile_path = ""
private_key_path = ""

download_threads = []


# default ytdlp options
yt_dlp_opts = {'extract_flat': 'discard_in_playlist',
               'fragment_retries': 10,
               'ignoreerrors': 'only_download',
               'postprocessors': [{'key': 'FFmpegConcat',
                                   'only_multi_video': True,
                                   'when': 'playlist'}],
               'retries': 10,
               'logger': Logger(),
               'noplaylist': True
               }


def about():
    """
    Opens up a new About messagebox.
    """
    messagebox.showinfo(
        "About YT-DLP-GUI", "YT-DLP-GUI: A graphical user interface for YT-DLP.\n" +
        "Developed by FlamingLeo, 2021 - 2024.\n\n" +
        f"Version {VERSION}, finished {DATE}.\nMade using Python and tkinter.\n\n" +
        "GitHub (YT-DLP): \nhttps://github.com/yt-dlp/yt-dlp")


def update_ytdlp():
    """
    Upgrades the yt-dlp module with pip.
    Not recommended.
    """
    pip.main(['install', '--upgrade', "yt_dlp"])
    insert_into_log("[pip] Updated yt_dlp... (pip install yt-dlp -U)")


def save_logs():
    """
    Saves the logs to an external text file in the same directory as the program.
    """
    try:
        if log_listbox.size():
            with open("logs.txt", "w") as file:
                for listbox_entry in enumerate(log_listbox.get(0, END)):
                    file.write(listbox_entry[1] + "\n")
    except:
        pass


def insert_into_log(msg):
    """
    Logs a message and moves the scrollbar to the bottom.
    """
    log_listbox.insert(END, msg)
    log_listbox.yview(END)


def log_if_option_chosen(opt, msg):
    """
    Logs a message if the parameter is chosen.
    """
    if opt.get():
        insert_into_log(msg)


def add_to_queue(link=None):
    """
    Adds valid URL to queue, either from link if passed as parameter 
    or from URL entry box if not empty.

    The queue cannot contain duplicate URLs.
    """
    url = (link if link != None else url_entry.get()).strip()
    if validators.url(url) and not url_queue.exists(url):
        hostname = '.'.join((urlparse(url).netloc).split('.')[-2:])
        url_queue.insert("", END, iid=url, values=(url, hostname))
        url_entry.delete(0, END)


def delete_from_queue(selection=None):
    """
    Deletes only selected URL from queue.
    """
    sel = selection if selection != None else url_queue.selection(
    )[0] if url_queue.selection() != () else None
    if sel:
        url_queue.delete(sel)


def clear_queue():
    """
    Clears the entire URL queue.
    """
    url_queue.delete(*url_queue.get_children())


def export_queue():
    """
    Exports URLs from queue to a text file.
    """
    try:
        urls = url_queue.get_children()
        if urls != ():
            with open("queue.txt", "w") as file:
                    for url in urls:
                        file.write(url + "\n")
    except:
        pass


def import_queue():
    """
    Loads URLs from text file into queue.
    Skips possible errors when opening / reading file.
    """
    url_file = filedialog.askopenfilename(initialdir="./")
    try:
        with open(url_file, "r") as file:
            for line in file:
                add_to_queue(line)
    except:
        pass


def entrybox_rightclick(option):
    """
    Performs a given action when choosing an option from the URL entry box
    right click menu. 

    p -> paste;
    pa -> paste and add;
    pd -> paste and download;
    c -> clear
    """
    match option:
        case "p":
            url_entry.delete(0, END)
            url_entry.insert(0, root.clipboard_get())
        case "pa":
            url_entry.delete(0, END)
            add_to_queue(root.clipboard_get())
        case "pd":
            url_entry.insert(0, root.clipboard_get())
            download()
        case "c":
            url_entry.delete(0, END)


def url_queue_rightclick(e):
    """
    URL queue rightclick menu.
    """
    global url_queue_selection
    url_queue_selection = url_queue.identify_row(e.y)
    url_queue_rightclickmenu.tk_popup(e.x_root, e.y_root)


def load_file(file):
    """
    Opens up a file dialog to load a certain file path.

    Currently supports loading download archive and cookie file.
    """
    match file:
        case "download_archive":
            global download_archive_path
            download_archive_path = filedialog.askopenfilename(initialdir="./")
            if download_archive_path:
                download_archive_label.config(text="Loaded download archive.")
                download_archive_button.config(
                    text="Reset Archive", command=lambda: reset_file("download_archive"))
        case "cookies":
            global cookie_file_path
            cookie_file_path = filedialog.askopenfilename(initialdir="./")
            if cookie_file_path:
                cookies_label.config(text="Loaded cookie file.")
                cookies_button.config(
                    text="Reset Cookies", command=lambda: reset_file("cookies"))
        case "certfile":
            global certfile_path
            certfile_path = filedialog.askopenfilename(initialdir="./")
            if certfile_path:
                certificate_client_label.config(
                    text="Loaded client certificate.")
                certificate_client_button.config(
                    text="Reset Certificate", command=lambda: reset_file("certfile"))
        case "keyfile":
            global private_key_path
            private_key_path = filedialog.askopenfilename(initialdir="./")
            if private_key_path:
                certificate_privatekey_label.config(
                    text="Loaded private key.")
                certificate_privatekey_button.config(
                    text="Reset Private Key", command=lambda: reset_file("keyfile"))


def reset_file(file):
    """
    Resets variables regarding settings stored in files.

    Currently supports resetting download archive and cookie file.
    """
    match file:
        case "download_archive":
            global download_archive_path
            download_archive_path = ""
            download_archive_label.config(
                text="No download archive specified.")
            download_archive_button.config(
                text="Open Archive", command=lambda: load_file("download_archive"))
        case "cookies":
            global cookie_file_path
            cookie_file_path = ""
            cookies_label.config(text="No cookie file specified.")
            cookies_button.config(
                text="Open Cookies", command=lambda: load_file("cookies"))
        case "certfile":
            global certfile_path
            certfile_path = ""
            certificate_client_label.config(
                text="No client certificate specified.")
            certificate_client_button.config(
                text="Open Certificate", command=lambda: load_file("certfile"))
        case "keyfile":
            global private_key_path
            private_key_path = ""
            certificate_privatekey_label.config(
                text="No private key specified.")
            certificate_privatekey_button.config(
                text="Open Private Key", command=lambda: load_file("keyfile"))


def insert_if_not_empty(entry, key, value):
    """
    Helper method to insert key-value pair into argument dictionary only if the
    corresponding entry is not empty.

    Otherwise, delete the existing entry.
    """
    if entry:
        yt_dlp_opts.update({key: value})
    else:
        yt_dlp_opts.pop(key, None)


def get_date():
    """
    Converts the date range input to a yt-dlp compatible DateRange object.

    start AND end -> DateRange(start, end)
    start OR end -> DateRange(date, date)
    ??? -> DateRange(20050101, today)
    """
    min_date = limits_daterange_min_entry.get()
    max_date = limits_daterange_max_entry.get()
    try:
        if min_date and max_date:
            return yt_dlp.DateRange(min_date, max_date)
        elif (min_date and (not max_date)):
            return yt_dlp.DateRange(min_date, min_date)
        elif ((not min_date) and max_date):
            return yt_dlp.DateRange(max_date, max_date)
        else:
            return yt_dlp.DateRange('20050101', 'today')
    except:
        return yt_dlp.DateRange('20050101', 'today')


def convert_to_number(value, fallback):
    """
    Helper method to convert number with prefixes to integer.
    For example, 50K becomes 50.000, 1M becomes 1.000.000 and so on.

    If the function fails, it returns a fallback value.
    """
    prefixes = {
        'K': 10**3,
        'M': 10**6,
        'B': 10**9
    }

    try:
        if value[-1].upper() in prefixes:
            prefix = value[-1].upper()
            number = float(value[:-1]) * prefixes[prefix]
            return int(number)
        else:
            return int(value)
    except:
        return fallback


def reset_postprocessors():
    """
    Resets the 'postprocessors' entry in yt_dlp_opts to default.
    """
    yt_dlp_opts.update({'postprocessors': [{'key': 'FFmpegConcat',
                                            'only_multi_video': True,
                                            'when': 'playlist'}]})


def check_parameters():
    """
    Checks ALL chosen parameters (entry boxes, radio boxes, dropdown menus...)
    and updates the yt-dlp option dictionary accordingly.
    """
    # verbosity
    yt_dlp_opts.update({"verbose": log_verbose.get()})

    # video: format
    # format_opt -> which format type to choose
    # format_name -> format as name (best, worst...)
    # format_filetype -> format as filetype (mp4, webm...)
    # only check validity for preset types; when using custom formats, leave error-handling to ytdlp
    reset_postprocessors()
    format_string = ""
    match format_opt.get():
        case 0:
            format_string = format_name.get()
        case 1:
            format_string = format_filetype.get()
        case 2:
            format_string = format_custom_entry.get().strip()
    if not format_string or format_string == "default":
        yt_dlp_opts.pop("format", None)
    else:
        yt_dlp_opts.update({"format": format_string})

    # video: metadata
    yt_dlp_opts.update({"writedescription": metadata_description.get()})
    yt_dlp_opts.update({"writeannotations": metadata_annotations.get()})
    yt_dlp_opts.update({"writethumbnail": metadata_thumbnail.get()})
    yt_dlp_opts.update({"writesubtitles": metadata_subtitles.get()})
    yt_dlp_opts.update({"writeautomaticsub": metadata_autosubtitles.get()})
    yt_dlp_opts.update({"writelink": metadata_url.get()})

    # video: limits
    insert_if_not_empty(limits_agelimit_entry.get(),
                        "age_limit", convert_to_number(limits_agelimit_entry.get(), 99))
    if limits_daterange_min_entry.get() or limits_daterange_max_entry.get():
        yt_dlp_opts.update({"daterange": get_date()})
    insert_if_not_empty(limits_viewrange_min_entry.get(
    ), "min_views", convert_to_number(limits_viewrange_min_entry.get(), 0))
    insert_if_not_empty(limits_viewrange_max_entry.get(), "max_views", convert_to_number(
        limits_viewrange_max_entry.get(), sys.maxsize))

    # video: output
    insert_if_not_empty(outputpath_entry.get(), "paths",
                        {"home": outputpath_entry.get()})
    insert_if_not_empty(outputoptions_entry.get(), "outtmpl",
                        {"default": outputoptions_entry.get()})

    # downloads: values
    insert_if_not_empty(download_ratelimit_entry.get(
    ), "ratelimit", convert_to_number(download_ratelimit_entry.get(), sys.maxsize))
    insert_if_not_empty(download_retries_entry.get(), "retries", convert_to_number(
        download_retries_entry.get(), sys.maxsize))
    insert_if_not_empty(download_fragments_entry.get(), "concurrent_fragment_downloads",
                        convert_to_number(download_fragments_entry.get(), sys.maxsize))
    insert_if_not_empty(download_max_downloads_entry.get(), "max_downloads",
                        convert_to_number(download_max_downloads_entry.get(), sys.maxsize))
    insert_if_not_empty(download_extractors_entry.get(), "allowed_extractors", list(
        map(lambda x: x.strip(), download_extractors_entry.get().split(","))))
    insert_if_not_empty(download_min_filesize_entry.get(), "min_filesize",
                        convert_to_number(download_min_filesize_entry.get(), 0))
    insert_if_not_empty(download_max_filesize_entry.get(), "max_filesize",
                        convert_to_number(download_max_filesize_entry.get(), sys.maxsize))

    # downloads: options
    # TODO: embed thumbnail
    yt_dlp_opts.update({"noplaylist": not download_include_playlist.get()})
    yt_dlp_opts.update({"keepvideo": download_keep_video.get()})
    yt_dlp_opts.update({"overwrites": download_overwrite.get()})

    if download_embed_subtitles.get():
        yt_dlp_opts['postprocessors'].append(
            {'already_have_subtitle': False, 'key': 'FFmpegEmbedSubtitle'})
        yt_dlp_opts.update({"writesubtitles": True})

    if download_embed_chapters.get():
        yt_dlp_opts['postprocessors'].append({'add_chapters': True,
                                              'add_infojson': None,
                                              'add_metadata': False,
                                              'key': 'FFmpegMetadata'})

    if download_split_chapters.get():
        yt_dlp_opts['postprocessors'].append(
            {'force_keyframes': False, 'key': 'FFmpegSplitChapters'})

    # networking: local
    insert_if_not_empty(download_archive_path,
                        "download_archive", download_archive_path)
    insert_if_not_empty(cookie_file_path, "cookiefile", cookie_file_path)

    # networking: connection
    # either ipv4, ipv6 or none can be chosen
    yt_dlp_opts.update({"legacyserverconnect": connection_legacy.get()})
    yt_dlp_opts.update({"prefer_insecure": connection_http.get()})
    yt_dlp_opts.update({"nocheckcertificate": connection_nossl.get()})
    yt_dlp_opts.update({"enable_file_urls": connection_fileurls.get()})
    if connection_ipv4:
        yt_dlp_opts.update({"source_address": "0.0.0.0"})
    elif connection_ipv6:
        yt_dlp_opts.update({"source_address": "::"})

    # networking: proxy
    insert_if_not_empty(proxy_entry.get(), "proxy", proxy_entry.get())
    insert_if_not_empty(client_ip_entry.get(),
                        "source_address", client_ip_entry.get())
    insert_if_not_empty(geo_proxy_entry.get(),
                        "geo_verification_proxy", geo_proxy_entry.get())
    insert_if_not_empty(geo_cc_entry.get(),
                        "geo_bypass_country", geo_cc_entry.get())

    # advanced: authentication
    # if username is specified, then include password automatically, even if empty
    if authentication_username_entry.get():
        yt_dlp_opts.update({"username": authentication_username_entry.get()})
        yt_dlp_opts.update({"password": authentication_password_entry.get()})
    insert_if_not_empty(authentication_2fa_entry.get(),
                        "twofactor", authentication_2fa_entry.get())
    insert_if_not_empty(authentication_videopwd_entry.get(),
                        "videopassword", authentication_videopwd_entry.get())
    yt_dlp_opts.update({"usenetrc": authentication_netrc.get()})

    # advanced: certificates
    insert_if_not_empty(certfile_path, "client_certificate", certfile_path)
    insert_if_not_empty(
        private_key_path, "client_certificate_key", private_key_path)
    insert_if_not_empty(certificate_password_entry.get(
    ), "client_certificate_password", certificate_password_entry.get())

    # advanced: post-processing
    # 1 -> audio
    # 2 -> remux
    # 3 -> recode
    match postprocessing_type.get():
        case 1:
            yt_dlp_opts.update({"final_ext": postprocessing_audio.get()})
            yt_dlp_opts.update({"format": "bestaudio/best"})
            yt_dlp_opts['postprocessors'].append({'key': 'FFmpegExtractAudio',
                                                  'nopostoverwrites': False,
                                                  'preferredcodec': postprocessing_audio.get(),
                                                  'preferredquality': '5'})
        case 2:
            yt_dlp_opts.update({"final_ext": postprocessing_remux.get()})
            yt_dlp_opts['postprocessors'].append(
                {'key': 'FFmpegVideoRemuxer', 'preferedformat': postprocessing_remux.get()})
        case 3:
            yt_dlp_opts.update({"final_ext": postprocessing_recode.get()})
            yt_dlp_opts['postprocessors'].append(
                {'key': 'FFmpegVideoConvertor', 'preferedformat': postprocessing_recode.get()})

    yt_dlp_opts.update({"fixup": postprocessing_fixup.get()})


def ytdl_download(urls):
    with yt_dlp.YoutubeDL(yt_dlp_opts) as ydl:
        download_thread = threading.Thread(
            target=ydl.download, args=[urls])
        download_thread.start()
        download_threads.append(download_thread)


def download():
    """
    Check parameters, then download URLs from queue using YT-DLP. Multithreaded.

    As a QoL improvement, if there is a valid URL in the entry box that hasn't been added
    to the queue, download it too without needing to add it to the queue. 
    """
    urls = url_queue.get_children()
    if url_entry.get() and validators.url(url_entry.get()):
        urls += (url_entry.get(), )
    if urls == ():
        if url_entry.get():
            insert_into_log("[ERROR] Invalid URL!")
        else:
            insert_into_log("[ERROR] URL queue empty!")
        return
    if url_queue_parallel.get() and len(urls) > CONCURRENT_LIMIT and not url_queue_parallel_warnings.get():
        if not messagebox.askokcancel("Large Amount of Parallel Downloads", f"You are trying to download more than {CONCURRENT_LIMIT} videos at once.\nThis may become unstable. Are you sure you want to continue?"):
            return
    check_parameters()
    clear_queue()
    url_entry.delete(0, END)
    if url_queue_parallel.get():
        for url in urls:
            download_url(url)
    else:
        try:
            ytdl_download(urls)
        except Exception as e:
            insert_into_log(f"[ERROR] {e}")


def download_url(link):
    """
    Check parameters, then download URL passed as parameter using YT-DLP. Multithreaded.
    """
    check_parameters()
    try:
        ytdl_download([link])
    except Exception as e:
        insert_into_log(f"[ERROR] {e}")


def ui_toggle_dropdowns(category):
    """
    Toggles enabled / disabled dropdowns in video selection tab based on radio button choice.

    0 -> name;
    1 -> filetype;
    2 -> custom;
    """
    match category:
        case "video":
            format_name_dropdown.config(
                state="readonly" if format_opt.get() == 0 else "disabled")
            format_filetype_dropdown.config(
                state="readonly" if format_opt.get() == 1 else "disabled")
            format_custom_entry.config(
                state="normal" if format_opt.get() == 2 else "disabled")
        case "advanced":
            postprocessing_audio_dropdown.config(
                state="readonly" if postprocessing_type.get() == 1 else "disabled")
            postprocessing_remux_dropdown.config(
                state="readonly" if postprocessing_type.get() == 2 else "disabled")
            postprocessing_recode_dropdown.config(
                state="readonly" if postprocessing_type.get() == 3 else "disabled")


def ui_toggle_ip(ipv):
    """
    Toggles IPv4 and IPv6 checkboxes such that either none or only one may be selected at once.
    """
    if ipv == 4:
        connection_ipv6.set(0)

    if ipv == 6:
        connection_ipv4.set(0)


def ui_insert_path():
    """
    Inserts the chosen path into the output path entry box.
    """
    outputpath = filedialog.askdirectory()
    if outputpath:
        outputpath_entry.delete(0, END)
        outputpath_entry.insert(0, outputpath)


def check_on_close():
    """
    Checks for active downloads on close.
    If there are still ongoing downloads, warn the user about closing the program.
    """
    running_threads = False
    for thread in download_threads:
        if thread.is_alive():
            running_threads = True
            break

    if running_threads:
        if messagebox.askokcancel("Ongoing Downloads", "There are still downloads in progress.\nAre you sure you want to quit?"):
            root.destroy()
    else:
        root.destroy()


def on_entry_click(entry, message):
    """
    Removes placeholder text specified in message parameter from given entrybox.
    """
    if entry.get() == message:
        entry.delete(0, END)
        entry.configure(foreground="black")


def on_focus_out(entry, message):
    """
    Adds placeholder text specified in message parameter from given entrybox.
    """
    if entry.get() == "":
        entry.insert(0, message)
        entry.configure(foreground="gray")


"""
TKinter logic begins here.
"""
root = Tk()
root.resizable(False, False)
root.title(f"YT-DLP-GUI {VERSION}")

# menu bar
menu_bar = Menu(root)
root.config(menu=menu_bar)

file_menu = Menu(menu_bar, tearoff=False)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Set Output Path", command=ui_insert_path)
file_menu.add_command(label="Download Test Video",
                      command=lambda: download_url(DUMMY_VIDEO))
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

url_menu = Menu(menu_bar, tearoff=False)
menu_bar.add_cascade(label="URL", menu=url_menu)
url_menu.add_command(label="Paste", command=lambda: entrybox_rightclick("p"))
url_menu.add_command(label="Paste and add to queue",
                     command=lambda: entrybox_rightclick("pa"))
url_menu.add_command(label="Paste and download",
                     command=lambda: entrybox_rightclick("pd"))
url_menu.add_command(label="Clear", command=lambda: entrybox_rightclick("c"))

queue_menu = Menu(menu_bar, tearoff=False)
menu_bar.add_cascade(label="Queue", menu=queue_menu)
queue_menu.add_command(label="Delete", command=lambda: delete_from_queue())
queue_menu.add_command(label="Import", command=import_queue)
queue_menu.add_command(label="Export", command=export_queue)
queue_menu.add_command(label="Clear", command=clear_queue)

logs_menu = Menu(menu_bar, tearoff=False)
menu_bar.add_cascade(label="Logs", menu=logs_menu)
logs_menu.add_command(label="Save Logs", command=save_logs)
logs_menu.add_command(label="Clear Logs",
                      command=lambda: log_listbox.delete(0, END))

help_menu = Menu(menu_bar, tearoff=False)
menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="Update YT-DLP", command=update_ytdlp)
help_menu.add_command(label="About", command=about)

# tabs
notebook = ttk.Notebook(root)
notebook.pack()

general_frame = Frame(notebook, width=400, height=400)
video_frame = Frame(notebook, width=400, height=400)
download_frame = Frame(notebook, width=400, height=400)
networking_frame = Frame(notebook, width=400, height=400)
advanced_frame = Frame(notebook, width=400, height=400)

general_frame.pack(fill="both", expand=1)
video_frame.pack(fill="both", expand=1)
download_frame.pack(fill="both", expand=1)
networking_frame.pack(fill="both", expand=1)
advanced_frame.pack(fill="both", expand=1)

notebook.add(general_frame, text="General")
notebook.add(video_frame, text="Video")
notebook.add(download_frame, text="Download")
notebook.add(networking_frame, text="Network")
notebook.add(advanced_frame, text="Advanced")

# dummy pixel for resizing buttons in pixel width
pixel = PhotoImage(width=1, height=1)

"""
GENERAL TAB:
- URL entry box
- URL queue (table)
- URL file importer
- downloader logs
"""

# url frame
url_frame = LabelFrame(general_frame, text="URLs", padx=5, pady=5)
url_frame.pack(padx=5, pady=5, fill=X, expand=1)

url_entry = ttk.Entry(url_frame, width=60)
url_entry.pack()

url_entry_rightclickmenu = Menu(url_entry, tearoff=False)
url_entry_rightclickmenu.add_command(
    label="Paste", command=lambda: entrybox_rightclick("p"))
url_entry_rightclickmenu.add_command(
    label="Paste and add to queue", command=lambda: entrybox_rightclick("pa"))
url_entry_rightclickmenu.add_command(
    label="Paste and download", command=lambda: entrybox_rightclick("pd"))
url_entry_rightclickmenu.add_command(
    label="Clear", command=lambda: entrybox_rightclick("c"))
url_entry.bind(
    "<Button-3>", lambda e: url_entry_rightclickmenu.tk_popup(e.x_root, e.y_root))

url_queue_frame = Frame(url_frame)
url_queue_frame.pack(padx=5, pady=5, fill=BOTH, expand=1, side=BOTTOM)
url_queue_scrollbar = ttk.Scrollbar(url_queue_frame)
url_queue_scrollbar.pack(side=RIGHT, fill=Y)
url_queue = ttk.Treeview(url_queue_frame, columns=(
    'title', 'src'), show='headings', selectmode="browse", height=3, yscrollcommand=url_queue_scrollbar.set)
url_queue.heading('title', text='URL')
url_queue.column('title', minwidth=20, width=265, stretch=FALSE)
url_queue.heading('src', text='Source')
url_queue.column('src', minwidth=20, width=80, stretch=False)
url_queue.pack()
url_queue_scrollbar.config(command=url_queue.yview)

url_queue_parallel_frame = Frame(url_frame)
url_queue_parallel_frame.pack(fill=BOTH, expand=1, side=BOTTOM)

url_queue_parallel = IntVar(value=0)
url_queue_parallel_warnings = IntVar(value=0)

url_queue_parallel_checkbutton = ttk.Checkbutton(
    url_queue_parallel_frame, text="Download Concurrently", variable=url_queue_parallel)
url_queue_parallel_checkbutton.pack(padx=5, side=LEFT)
url_queue_parallel_warnings_checkbutton = ttk.Checkbutton(
    url_queue_parallel_frame, text="Supress Warnings", variable=url_queue_parallel_warnings)
url_queue_parallel_warnings_checkbutton.pack(padx=5, side=RIGHT)

url_queue_rightclickmenu = Menu(url_queue, tearoff=False)
url_queue_rightclickmenu.add_command(
    label="Delete", command=lambda: delete_from_queue(url_queue_selection))
url_queue_rightclickmenu.add_command(
    label="Import", command=import_queue)
url_queue_rightclickmenu.add_command(
    label="Export", command=export_queue)
url_queue_rightclickmenu.add_command(label="Clear", command=clear_queue)
url_queue.bind("<Button-3>", url_queue_rightclick)

url_add_button = ttk.Button(url_frame, text="Add",
                            image=pixel, compound="c", width=13, command=add_to_queue)
url_add_button.pack(padx=(5, 0), pady=(5, 0), side=LEFT)
url_remove_button = ttk.Button(
    url_frame, text="Remove", image=pixel, compound="c", width=14, command=delete_from_queue)
url_remove_button.pack(pady=(5, 0), side=LEFT)
url_import_button = ttk.Button(
    url_frame, text="Import", image=pixel, compound="c", width=14, command=import_queue)
url_import_button.pack(padx=(0, 5), pady=(5, 0), side=RIGHT)
url_clear_button = ttk.Button(
    url_frame, text="Clear", image=pixel, compound="c", width=13, command=clear_queue)
url_clear_button.pack(pady=(5, 0), side=RIGHT)

# output logs
log_frame = LabelFrame(general_frame, text="Logs", padx=5, pady=5)
log_frame.pack(padx=5, pady=5, fill=X, expand=1)
log_frame_inner = Frame(log_frame)
log_frame_inner.pack()
log_frame_scrollbar = ttk.Scrollbar(log_frame_inner)
log_frame_scrollbar.pack(side=RIGHT, fill=Y)
log_listbox = Listbox(log_frame_inner, width=58, height=5,
                      yscrollcommand=log_frame_scrollbar.set)
log_listbox.pack()

log_rightclickmenu = Menu(url_entry, tearoff=False)
log_rightclickmenu.add_command(
    label="Save", command=save_logs)
log_rightclickmenu.add_command(
    label="Clear", command=lambda: log_listbox.delete(0, END))
log_listbox.bind(
    "<Button-3>", lambda e: log_rightclickmenu.tk_popup(e.x_root, e.y_root))

log_info = IntVar(value=1)
log_warn = IntVar(value=1)
log_err = IntVar(value=1)
log_verbose = IntVar(value=0)

log_info_checkbox = ttk.Checkbutton(
    log_frame, text="Information", variable=log_info, state=DISABLED)
log_info_checkbox.pack(padx=5, side=LEFT)
log_warnings_checkbox = ttk.Checkbutton(
    log_frame, text="Warnings", variable=log_warn)
log_warnings_checkbox.pack(padx=5, side=LEFT)
log_error_checkbox = ttk.Checkbutton(
    log_frame, text="Errors", variable=log_err)
log_error_checkbox.pack(padx=5, side=LEFT)
log_verbose_checkbox = ttk.Checkbutton(
    log_frame, text="Verbose", variable=log_verbose)
log_verbose_checkbox.pack(padx=5, side=LEFT)

download_button = ttk.Button(
    general_frame, text="Download", image=pixel, compound="c", width=63, command=download)
download_button.pack(padx=5, pady=5)

"""
VIDEO TAB:
- format settings (best / worst, file formats, custom)
- metadata options (description, comments, thumbnail, link, subtitles etc.)
- limits (date range, age limit, min / max view count)
- set path and output name template
"""

# format options
format_frame = LabelFrame(video_frame, text="Format Settings", padx=5, pady=5)
format_frame.pack(padx=5, pady=5, fill=X, expand=1, anchor=N)
format_frame.grid_columnconfigure(0, weight=1)

format_opt = IntVar()
format_name = StringVar()
format_filetype = StringVar()

format_name_radio = ttk.Radiobutton(
    format_frame, text="Format by Name", variable=format_opt, value=0, command=lambda: ui_toggle_dropdowns("video"))
format_filetype_radio = ttk.Radiobutton(
    format_frame, text="Format by Filetype", variable=format_opt, value=1, command=lambda: ui_toggle_dropdowns("video"))
format_custom_radio = ttk.Radiobutton(
    format_frame, text="Custom Format", variable=format_opt, value=2, command=lambda: ui_toggle_dropdowns("video"))
format_name_radio.grid(padx=5, sticky=W, row=0, column=0)
format_filetype_radio.grid(padx=5, sticky=W, row=1, column=0)
format_custom_radio.grid(padx=5, sticky=W, row=2, column=0)

format_name_dropdown = ttk.Combobox(
    format_frame, state="readonly", width=35, textvariable=format_name, values=FORMAT_NAMES)
format_name_dropdown.current(0)
format_name_dropdown.grid(padx=5, sticky=E, row=0, column=1)
format_filetype_dropdown = ttk.Combobox(
    format_frame, state=DISABLED, width=35, textvariable=format_filetype, values=FORMAT_FILETYPES)
format_filetype_dropdown.current(0)
format_filetype_dropdown.grid(padx=5, sticky=E, row=1, column=1)
format_custom_entry = ttk.Entry(format_frame, width=38, state=DISABLED)
format_custom_entry.grid(padx=5, sticky=E, row=2, column=1)

# metadata options
metadata_frame = LabelFrame(video_frame, text="Metadata", padx=5, pady=5)
metadata_frame.pack(padx=5, pady=5, fill=X, expand=1)
metadata_frame.grid_columnconfigure(0, weight=1)

metadata_description = IntVar()
metadata_annotations = IntVar()
metadata_thumbnail = IntVar()
metadata_subtitles = IntVar()
metadata_autosubtitles = IntVar()
metadata_url = IntVar()

metadata_description_checkbox = ttk.Checkbutton(
    metadata_frame, text="Download Description", variable=metadata_description)
metadata_description_checkbox.grid(padx=5, sticky=W, row=0, column=0)
metadata_annotations_checkbox = ttk.Checkbutton(
    metadata_frame, text="Download Annotations", variable=metadata_annotations)
metadata_annotations_checkbox.grid(padx=5, sticky=W, row=0, column=1)
metadata_thumbnail_checkbox = ttk.Checkbutton(
    metadata_frame, text="Download Thumbnail", variable=metadata_thumbnail)
metadata_thumbnail_checkbox.grid(padx=5, sticky=W, row=1, column=0)
metadata_subtitles_checkbox = ttk.Checkbutton(
    metadata_frame, text="Download Subtitles", variable=metadata_subtitles)
metadata_subtitles_checkbox.grid(padx=5, sticky=W, row=1, column=1)
metadata_autosubtitles_checkbox = ttk.Checkbutton(
    metadata_frame, text="Download Automatic Subtitles", variable=metadata_autosubtitles)
metadata_autosubtitles_checkbox.grid(padx=5, sticky=W, row=2, column=0)
metadata_url_checkbox = ttk.Checkbutton(
    metadata_frame, text="Download Video URL", variable=metadata_url)
metadata_url_checkbox.grid(padx=5, sticky=W, row=2, column=1)

# limit options
limits_frame = LabelFrame(video_frame, text="Limits", padx=5, pady=5)
limits_frame.pack(padx=5, pady=5, fill=X, expand=1)
limits_frame.grid_columnconfigure(0, weight=1)

limits_daterange_label = Label(limits_frame, text="Date Range: ")
limits_daterange_label.grid(padx=5, sticky=W, row=0, column=0)
limits_agelimit_label = Label(limits_frame, text="Age Limit: ")
limits_agelimit_label.grid(padx=5, sticky=W, row=1, column=0)
limits_viewrange_label = Label(limits_frame, text="View Count Range: ")
limits_viewrange_label.grid(padx=5, sticky=W, row=2, column=0)

limits_daterange_min_text = "From (YYYYMMDD)"
limits_daterange_max_text = "To (YYYYMMDD)"

limits_daterange_min_entry = ttk.Entry(
    limits_frame, width=18, foreground="gray")
limits_daterange_min_entry.insert(0, limits_daterange_min_text)
limits_daterange_min_entry.bind("<FocusIn>", lambda e: on_entry_click(
    limits_daterange_min_entry, limits_daterange_min_text))
limits_daterange_min_entry.bind("<FocusOut>", lambda e: on_focus_out(
    limits_daterange_min_entry, limits_daterange_min_text))
limits_daterange_min_entry.grid(padx=5, sticky=E, row=0, column=1)
limits_daterange_max_entry = ttk.Entry(
    limits_frame, width=18, foreground="gray")
limits_daterange_max_entry.insert(0, limits_daterange_max_text)
limits_daterange_max_entry.bind("<FocusIn>", lambda e: on_entry_click(
    limits_daterange_max_entry, limits_daterange_max_text))
limits_daterange_max_entry.bind("<FocusOut>", lambda e: on_focus_out(
    limits_daterange_max_entry, limits_daterange_max_text))
limits_daterange_max_entry.grid(padx=5, sticky=E, row=0, column=2)
limits_agelimit_entry = ttk.Entry(limits_frame, width=39)
limits_agelimit_entry.grid(padx=5, sticky=E, row=1, column=1, columnspan=2)
limits_viewrange_min_entry = ttk.Entry(limits_frame, width=18)
limits_viewrange_min_entry.grid(padx=5, sticky=E, row=2, column=1)
limits_viewrange_max_entry = ttk.Entry(limits_frame, width=18)
limits_viewrange_max_entry.grid(padx=5, sticky=W, row=2, column=2)


# output and path options
output_frame = LabelFrame(video_frame, text="Output Options", padx=5, pady=5)
output_frame.pack(padx=5, pady=5, fill=X, expand=1)
output_frame.grid_columnconfigure(0, weight=1)

outputpath_label = Label(output_frame, text="Output Path: ")
outputpath_label.grid(padx=5, sticky=W, row=0, column=0)
outputoptions_label = Label(output_frame, text="Output Options: ")
outputoptions_label.grid(padx=5, sticky=W, row=1, column=0)
outputpath_entry = ttk.Entry(output_frame, width=26)
outputpath_entry.insert(0, os.path.abspath(os.getcwd()).replace(os.sep, '/'))
outputpath_entry.grid(padx=5, sticky=E, row=0, column=1)
outputpath_button = ttk.Button(
    output_frame, text="Browse", command=ui_insert_path)
outputpath_button.grid(padx=5, sticky=E, row=0, column=2)
outputoptions_entry = ttk.Entry(output_frame, width=41)
outputoptions_entry.grid(padx=5, sticky=E, row=1, column=1, columnspan=2)

"""
DOWNLOAD TAB:
- download values (options with arguments)
- download options (options without arguments)
"""

# download values
download_values_frame = LabelFrame(
    download_frame, text="Downloader Values", padx=5, pady=5)
download_values_frame.pack(padx=5, pady=5, fill=X, expand=1, anchor=N)
download_values_frame.grid_columnconfigure(0, weight=1)

download_ratelimit_label = Label(
    download_values_frame, text="Maximum Download Rate: ")
download_ratelimit_label.grid(padx=5, sticky=W, row=0, column=0)
download_retries_label = Label(
    download_values_frame, text="Number of Retries: ")
download_retries_label.grid(padx=5, sticky=W, row=1, column=0)
download_fragments_label = Label(
    download_values_frame, text="Concurrent Fragments: ")
download_fragments_label.grid(padx=5, sticky=W, row=2, column=0)
download_max_downloads_label = Label(download_values_frame,
                                     text="Max. Number of Downloads: ")
download_max_downloads_label.grid(padx=5, sticky=W, row=3, column=0)
download_extractors_label = Label(
    download_values_frame, text="Allowed Extractors: ")
download_extractors_label.grid(padx=5, sticky=W, row=4, column=0)
download_min_filesize_label = Label(
    download_values_frame, text="Minimum Filesize: ")
download_min_filesize_label.grid(padx=5, sticky=W, row=5, column=0)
download_max_filesize_label = Label(
    download_values_frame, text="Maximum Filesize: ")
download_max_filesize_label.grid(padx=5, sticky=W, row=6, column=0)

download_ratelimit_entry = ttk.Entry(download_values_frame, width=31)
download_ratelimit_entry.grid(padx=5, sticky=E, row=0, column=1)
download_retries_entry = ttk.Entry(download_values_frame, width=31)
download_retries_entry.grid(padx=5, sticky=E, row=1, column=1)
download_fragments_entry = ttk.Entry(download_values_frame, width=31)
download_fragments_entry.grid(padx=5, sticky=E, row=2, column=1)
download_max_downloads_entry = ttk.Entry(download_values_frame, width=31)
download_max_downloads_entry.grid(padx=5, sticky=E, row=3, column=1)
download_extractors_entry = ttk.Entry(download_values_frame, width=31)
download_extractors_entry.grid(padx=5, sticky=E, row=4, column=1)
download_min_filesize_entry = ttk.Entry(download_values_frame, width=31)
download_min_filesize_entry.grid(padx=5, sticky=E, row=5, column=1)
download_max_filesize_entry = ttk.Entry(download_values_frame, width=31)
download_max_filesize_entry.grid(padx=5, sticky=E, row=6, column=1)

# download options
download_options_frame = LabelFrame(
    download_frame, text="Downloader Options", padx=5, pady=5)
download_options_frame.pack(padx=5, pady=5, fill=X, expand=1)

download_include_playlist = IntVar()
download_keep_video = IntVar()
download_overwrite = IntVar()
download_embed_subtitles = IntVar()
download_embed_chapters = IntVar()
download_embed_thumbnail = IntVar()
download_split_chapters = IntVar()

download_no_playlist_radio = ttk.Radiobutton(
    download_options_frame, text="Download only video if playlist included in URL", variable=download_include_playlist, value=False)
download_no_playlist_radio.pack(padx=5, anchor=W)
download_yes_playlist_radio = ttk.Radiobutton(
    download_options_frame, text="Download playlist if playlist included in URL", variable=download_include_playlist, value=True)
download_yes_playlist_radio.pack(padx=5, anchor=W)
download_keep_video_checkbox = ttk.Checkbutton(
    download_options_frame, text="Keep Intermediate Video", variable=download_keep_video)
download_keep_video_checkbox.pack(padx=5, anchor=W)
download_overwrite_checkbox = ttk.Checkbutton(
    download_options_frame, text="Overwrite Downloads", variable=download_overwrite)
download_overwrite_checkbox.pack(padx=5, anchor=W)
download_embed_subtitles_checkbox = ttk.Checkbutton(
    download_options_frame, text="Embed Subtitles in Video File (mp4, webm, mkv)", variable=download_embed_subtitles)
download_embed_subtitles_checkbox.pack(padx=5, anchor=W)
download_embed_thumbnail_checkbox = ttk.Checkbutton(
    download_options_frame, text="Embed Thumbnail in Video File", variable=download_embed_thumbnail, state=DISABLED)
download_embed_thumbnail_checkbox.pack(padx=5, anchor=W)
download_embed_chapters_checkbox = ttk.Checkbutton(
    download_options_frame, text="Embed Chapters in Video File", variable=download_embed_chapters)
download_embed_chapters_checkbox.pack(padx=5, anchor=W)
download_split_chapters_checkbox = ttk.Checkbutton(
    download_options_frame, text="Split Video based on Chapters", variable=download_split_chapters)
download_split_chapters_checkbox.pack(padx=5, anchor=W)

"""
NETWORK TAB:
- store and load download archive, cookies
- connection settings (ssl, https, ipv4/6)
- proxy and geobypass settings
"""

# local settings saved on disk
file_settings_frame = LabelFrame(
    networking_frame, text="Local Settings", padx=5, pady=5)
file_settings_frame.pack(padx=5, pady=5, fill=X, expand=1, anchor=N)

download_archive_label = Label(
    file_settings_frame, text="No download archive specified.")
download_archive_label.pack()
cookies_label = Label(file_settings_frame, text="No cookie file specified.")
cookies_label.pack()

download_archive_button = ttk.Button(
    file_settings_frame, text="Open Archive", image=pixel, compound="c", width=20, command=lambda: load_file("download_archive"))
download_archive_button.pack(padx=(50, 0), side=LEFT)
cookies_button = ttk.Button(
    file_settings_frame, text="Open Cookies", image=pixel, compound="c", width=20, command=lambda: load_file("cookies"))
cookies_button.pack(padx=(0, 50), side=RIGHT)

# connection settings
connection_settings_frame = LabelFrame(
    networking_frame, text="Connection Settings", padx=5, pady=5)
connection_settings_frame.pack(padx=5, pady=5, fill=X, expand=1)

connection_legacy = IntVar()
connection_http = IntVar()
connection_nossl = IntVar()
connection_fileurls = IntVar()
connection_ipv4 = IntVar()
connection_ipv6 = IntVar()

connection_legacy_checkbox = ttk.Checkbutton(
    connection_settings_frame, text="Allow HTTPS connection to servers that don't support RFC 5746", variable=connection_legacy)
connection_legacy_checkbox.pack(padx=5, anchor=W)
connection_http_checkbox = ttk.Checkbutton(
    connection_settings_frame, text="Use HTTP instead of HTTPS (possibly unsupported)", variable=connection_http)
connection_http_checkbox.pack(padx=5, anchor=W)
connection_nossl_checkbox = ttk.Checkbutton(
    connection_settings_frame, text="Do not check SSL certificates", variable=connection_nossl)
connection_nossl_checkbox.pack(padx=5, anchor=W)
connection_fileurls_checkbox = ttk.Checkbutton(
    connection_settings_frame, text="Allow file:// URLs", variable=connection_fileurls)
connection_fileurls_checkbox.pack(padx=5, anchor=W)
connection_ipv4_checkbox = ttk.Checkbutton(
    connection_settings_frame, text="Force IPv4", variable=connection_ipv4, command=lambda: ui_toggle_ip(4))
connection_ipv4_checkbox.pack(padx=5, anchor=W)
connection_ipv6_checkbox = ttk.Checkbutton(
    connection_settings_frame, text="Force IPv6", variable=connection_ipv6, command=lambda: ui_toggle_ip(6))
connection_ipv6_checkbox.pack(padx=5, anchor=W)

# proxy and geobypass settings
proxy_frame = LabelFrame(
    networking_frame, text="Proxy and Geobypass Settings", padx=5, pady=5)
proxy_frame.pack(padx=5, pady=5, fill=X, expand=1)
proxy_frame.grid_columnconfigure(0, weight=1)

proxy_label = Label(proxy_frame, text="Proxy URL:")
proxy_label.grid(padx=5, sticky=W, row=0, column=0)
client_ip_label = Label(proxy_frame, text="Client-Side IP:")
client_ip_label.grid(padx=5, sticky=W, row=1, column=0)
geo_proxy_label = Label(proxy_frame, text="Geoverification Proxy URL:")
geo_proxy_label.grid(padx=5, sticky=W, row=2, column=0)
geo_cc_label = Label(proxy_frame, text="Geobypass ISO 3166-2 CC:")
geo_cc_label.grid(padx=5, sticky=W, row=3, column=0)

proxy_entry = ttk.Entry(proxy_frame, width=33)
proxy_entry.grid(padx=5, sticky=E, row=0, column=1)
client_ip_entry = ttk.Entry(proxy_frame, width=33)
client_ip_entry.grid(padx=5, sticky=E, row=1, column=1)
geo_proxy_entry = ttk.Entry(proxy_frame, width=33)
geo_proxy_entry.grid(padx=5, sticky=E, row=2, column=1)
geo_cc_entry = ttk.Entry(proxy_frame, width=33)
geo_cc_entry.grid(padx=5, sticky=E, row=3, column=1)

"""
ADVANCED TAB:
- remux options
- authentication options
"""

# authentication options
authentication_frame = LabelFrame(
    advanced_frame, text="Authentication", padx=5, pady=5)
authentication_frame.pack(padx=5, pady=5, fill=X, expand=1, anchor=N)
authentication_frame.grid_columnconfigure(0, weight=1)

authentication_username_label = Label(authentication_frame, text="Username")
authentication_username_label.grid(padx=5, sticky=W, row=0, column=0)
authentication_password_label = Label(authentication_frame, text="Password")
authentication_password_label.grid(padx=5, sticky=W, row=1, column=0)
authentication_2fa_label = Label(authentication_frame, text="2FA Code")
authentication_2fa_label.grid(padx=5, sticky=W, row=2, column=0)
authentication_videopwd_label = Label(
    authentication_frame, text="Video Password")
authentication_videopwd_label.grid(padx=5, sticky=W, row=3, column=0)

authentication_username_entry = ttk.Entry(authentication_frame, width=41)
authentication_username_entry.grid(padx=5, sticky=E, row=0, column=1)
authentication_password_entry = ttk.Entry(
    authentication_frame, width=41, show="*")
authentication_password_entry.grid(padx=5, sticky=E, row=1, column=1)
authentication_2fa_entry = ttk.Entry(authentication_frame, width=41)
authentication_2fa_entry.grid(padx=5, sticky=E, row=2, column=1)
authentication_videopwd_entry = ttk.Entry(
    authentication_frame, width=41, show="*")
authentication_videopwd_entry.grid(padx=5, sticky=E, row=3, column=1)

authentication_netrc = IntVar()

authentication_netrc_checkbox = ttk.Checkbutton(
    authentication_frame, text="Use .netrc authentication data (~/.netrc)", variable=authentication_netrc)
authentication_netrc_checkbox.grid(
    padx=5, sticky=W, row=4, column=0, columnspan=2)

# certificates
certificate_frame = LabelFrame(
    advanced_frame, text="Certificates", padx=5, pady=5)
certificate_frame.pack(padx=5, pady=5, fill=X, expand=1)
certificate_frame.grid_columnconfigure(0, weight=1)

certificate_client_label = Label(
    certificate_frame, text="No client certificate specified.")
certificate_client_label.grid(padx=5, row=0, column=0, sticky=W)
certificate_privatekey_label = Label(
    certificate_frame, text="No private key specified.")
certificate_privatekey_label.grid(padx=5, row=1, column=0, sticky=W)
certificate_password_label = Label(
    certificate_frame, text="Certificate Password:")
certificate_password_label.grid(padx=5, row=2, column=0, sticky=W)

certificate_client_button = ttk.Button(
    certificate_frame, text="Open Certificate", image=pixel, compound="c", width=30, command=lambda: load_file("certfile"))
certificate_client_button.grid(padx=5, row=0, column=1, sticky=E)
certificate_privatekey_button = ttk.Button(
    certificate_frame, text="Open Private Key", image=pixel, compound="c", width=30, command=lambda: load_file("keyfile"))
certificate_privatekey_button.grid(padx=5, row=1, column=1, sticky=E)

certificate_password_entry = ttk.Entry(certificate_frame, width=31, show="*")
certificate_password_entry.grid(padx=5, row=2, column=1, sticky=E)

# post-processing
postprocessing_frame = LabelFrame(
    advanced_frame, text="Post-Processing", padx=5, pady=5)
postprocessing_frame.pack(padx=5, pady=5, fill=X, expand=1)
postprocessing_frame.grid_columnconfigure(0, weight=1)

postprocessing_type = IntVar()
postprocessing_audio = StringVar()
postprocessing_remux = StringVar()
postprocessing_recode = StringVar()
postprocessing_fixup = StringVar()

postprocessing_default_radio = ttk.Radiobutton(
    postprocessing_frame, text="Do Nothing", variable=postprocessing_type, value=0, command=lambda: ui_toggle_dropdowns("advanced"))
postprocessing_audio_radio = ttk.Radiobutton(
    postprocessing_frame, text="Extract Audio", variable=postprocessing_type, value=1, command=lambda: ui_toggle_dropdowns("advanced"))
postprocessing_remux_radio = ttk.Radiobutton(
    postprocessing_frame, text="Remux Video", variable=postprocessing_type, value=2, command=lambda: ui_toggle_dropdowns("advanced"))
postprocessing_recode_radio = ttk.Radiobutton(
    postprocessing_frame, text="Recode Video", variable=postprocessing_type, value=3, command=lambda: ui_toggle_dropdowns("advanced"))
postprocessing_default_radio.grid(padx=5, sticky=W, row=0, column=0)
postprocessing_audio_radio.grid(padx=5, sticky=W, row=1, column=0)
postprocessing_remux_radio.grid(padx=5, sticky=W, row=2, column=0)
postprocessing_recode_radio.grid(padx=5, sticky=W, row=3, column=0)

postprocessing_audio_dropdown = ttk.Combobox(
    postprocessing_frame, state=DISABLED, width=35, textvariable=postprocessing_audio, values=AUDIO_FORMATS)
postprocessing_audio_dropdown.current(0)
postprocessing_audio_dropdown.grid(padx=5, sticky=E, row=1, column=1)
postprocessing_remux_dropdown = ttk.Combobox(
    postprocessing_frame, state=DISABLED, width=35, textvariable=postprocessing_remux, values=REMUX_RECODE_FORMATS)
postprocessing_remux_dropdown.current(0)
postprocessing_remux_dropdown.grid(padx=5, sticky=E, row=2, column=1)
postprocessing_recode_dropdown = ttk.Combobox(
    postprocessing_frame, state=DISABLED, width=35, textvariable=postprocessing_recode, values=REMUX_RECODE_FORMATS)
postprocessing_recode_dropdown.current(0)
postprocessing_recode_dropdown.grid(padx=5, sticky=E, row=3, column=1)

postprocessing_fixup_label = Label(postprocessing_frame, text="Fixup Policy")
postprocessing_fixup_label.grid(padx=5, sticky=W, row=4, column=0)
postprocessing_fixup_dropdown = ttk.Combobox(
    postprocessing_frame, state="readonly", width=35, textvariable=postprocessing_fixup, values=FIXUP_POLICIES)
postprocessing_fixup_dropdown.current(0)
postprocessing_fixup_dropdown.grid(padx=5, sticky=E, row=4, column=1)

"""
DONE!
"""
root.protocol("WM_DELETE_WINDOW", check_on_close)
root.mainloop()
