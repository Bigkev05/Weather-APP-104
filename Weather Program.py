# Built-in library modules
from sqlite3 import *
import datetime
from tkinter import ttk
import re
import os
import os.path as path
import tkinter as tk

# custom modules
from download_util import *
from broswer_util import *
from db_util import *

# Authorship
STUDENT_NAME = 'Kevin Trinh'
STUDENT_NUMBER = 'n12034762'

# links and database
DATABASE_NAME = "radar_app.db"
RADAR_URL = "ftp://ftp.bom.gov.au/anon/gen/radar/"
BACKGROUND_URL = 'ftp://ftp.bom.gov.au/anon/gen/radar_transparencies/'

# file constants 
INDEX_FILE_NAME = "radar_index.txt"
RADAR_FILE_NAME = "image_index.txt"
LOG_FILE_NAME = "event_log.html"

# image adjustments and time
RADAR_IMAGE_WIDTH = 520
RADAR_IMAGE_HEIGHT = 560
MAX_SECONDS = 60

# SQL queries 
SELECT_RADAR_INFO = "SELECT RadarId, RadarName FROM Radars"
SELECT_LOG_INFO = "SELECT EventType, DateTime, Details FROM Log"
INSERT_LOG_INFO = "INSERT INTO Log VALUES(?, ?, ?)"


#<----------------------------------------------------------------------------------------------------------------------------------------------------------------------
def download_radar_url() -> None:
    '''
    Downloads the radar index file if it does not exist or is older than 60 seconds.
    
    '''
    if path.exists(INDEX_FILE_NAME):
        # get the last modified time of the file
        last_modified_time = path.getmtime(INDEX_FILE_NAME)
        current_time = datetime.datetime.now().timestamp()

        # check if the file is older than 60 seconds
        if current_time - last_modified_time <= MAX_SECONDS:
            print(f"{INDEX_FILE_NAME} is up to date at {current_time}")
            return

    # If the file does not exist or is older than 60 seconds, download a new copy
    download_file(RADAR_URL, INDEX_FILE_NAME)
    print(f"{path.getsize(INDEX_FILE_NAME)} bytes saved to {INDEX_FILE_NAME}")

def download_radar_transparencies_url() -> None:
    '''
    Downloads the image index file if it does not exist or is older than 60 seconds.
    '''
    if path.exists(RADAR_FILE_NAME):
        # get the last modified time of the file
        last_modified_time = path.getmtime(RADAR_FILE_NAME)
        current_time = datetime.datetime.now().timestamp()

        # check if the file is older than 60 seconds 
        if current_time - last_modified_time <= MAX_SECONDS:
            print(f"{RADAR_FILE_NAME} is up to date at {current_time}")
            return
    download_file(BACKGROUND_URL, RADAR_FILE_NAME)
    print(f"{path.getsize(RADAR_FILE_NAME)} bytes saved to {RADAR_FILE_NAME}")

def log_event_db(event: str, details: str) -> None:
    '''
    Logs an event to the radar_app database or specifically

    Parameters:
    event_type: Type of the event
    details: Details of the event

    returns: 
    none: logs the event from an activity in the interface

    '''
    connection = connect(DATABASE_NAME)
    cursor = connection.cursor()
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(INSERT_LOG_INFO, (event, time, details))
    connection.commit()
    connection.close()

def generate_weather_report():
    ''''
    Generates an HTML report of event log information.

    Reads event log data from the database and writes it into an HTML file.

    '''
    # Connect to the database
    connection = connect(DATABASE_NAME)
    cursor = connection.cursor()

    # Execute SQL query to fetch event log information
    cursor.execute(SELECT_LOG_INFO)
    log_info = cursor.fetchall()

    # Open the HTML report file in write mode
    with open(LOG_FILE_NAME, 'w') as report_file:
        # Write HTML header and title
        report_file.write("<html>\n")
        report_file.write("<head><title>Weather Log Report</title></head>\n")
        report_file.write("<body>\n")
        report_file.write("<h1>Weather Log Report</h1>\n")

        # Write table header
        report_file.write("<table border='1'>\n")
        report_file.write("<tr><th>Event Type</th><th>Date and Time</th><th>Details</th></tr>\n")

        # Write event log data to the table
        for event in log_info:
            report_file.write(f"<tr><td>{event[0]}</td><td>{event[1]}</td><td>{event[2]}</td></tr>\n")

        # Close the table and body tags
        report_file.write("</table>\n")
        report_file.write("</body>\n")
        report_file.write("</html>")
    
    # Print success message
    print(f"Event log report generated - {LOG_FILE_NAME}")


def display_weather_report() -> print:
    '''
    Displays the generated event log report in a web browser.
    '''
    generate_weather_report()
    open_html_file(LOG_FILE_NAME)
    print("Successfully opened event log report")

def radar_station_select(event:str) -> None:
    '''
    Handles the event of selecting a radar station from the radar station list.

    Parameters:
    event: The event object triggered by the selection. When first treeview clicked
           display the radar weather image list from the radar_index file
           it will find the matching radar ID from the radar_app db and radar_index file
           if match, it will find the rest of the data by using forloop method and
           using the capturing group method for re to match.

    returns: 
    none: logs the event and find matching re to display in treeview

    '''
    # Retrieve the selected item from the radar list
    selected_radar_station = event.widget.selection()
    if selected_radar_station:

        # Extract radar ID and name from the selected item
        item_values = event.widget.item(selected_radar_station)['values']
        radar_id, radar_name = item_values

        # Log the radar selection event
        log_event_db("SelectRadar", f"Selected {radar_id}:{radar_name}")
        # Read the contents of the radar index file
        with open(INDEX_FILE_NAME, 'r') as index_file:
            Index_file_data = index_file.read()
            
            # regular expression to extract required info from index data
            # example extraction: IDR012.T.202405161124.png
            image_pattern = r'(IDR\d{3})\.T\.(\d{12})\.png'
            png_matches = re.findall(image_pattern, Index_file_data)

            # clear existing entries in the radar image timestamps table
            table2.delete(*table2.get_children())

            # Iterate through png_matches and insert timestamp data into the table
            for match in png_matches:

                # first group of the image_pattern to equal radar_ID from radar station
                # example - (IDR\d{3})
                if match[0] == radar_id:

                    # extract timestamp and format date and time using the second group of image_pattern
                    # example - (\d{12})
                    timestamp_str = match[1]
                    timestamp = datetime.datetime.strptime(timestamp_str, "%Y%m%d%H%M")
                    date = timestamp.date().isoformat()
                    time_formatted = timestamp.time().strftime("%H:%M")

                    # Insert timestamp data into the table
                    table2.insert("", tk.END, values=(radar_id, date, time_formatted))



def radar_image_display(event: str) -> None:
    """
    Handles the event of selecting a radar image which will
    display multiple images from the radar image list.

    Parameters:
    event: The event object triggered by the selection: when clicked second 
            treeview , It will display 5 images which is legend, background,
            radar, location, range in one canvas which will be download from
            link.

    returns: 
    none: logs the event and update the interface with download image
          files and changes the interface

    """
    # Retrieve the selected item from the image_index list
    select_radar_image = event.widget.selection()
    if select_radar_image:
        item_values = event.widget.item(select_radar_image)['values']
        radar_id, date, time_formatted = item_values

        # Using regular expressions (re.sub) to remove dashes and colons from the date and time formatted strings
        date_cleaned = re.sub(r'-', '', date)
        time_cleaned = re.sub(r':', '', time_formatted)
        image_name = f"{radar_id}.T.{date_cleaned}{time_cleaned}.png"

        # full path to the image file
        image_path = os.path.join(os.getcwd(), image_name)

        # check if the image file already exists
        if not os.path.exists(image_path):
            image_url = f"{RADAR_URL}/{image_name}"
            log_event_db("ViewImage", f"Viewing image {image_name}")
            download_file(image_url, image_name)

        # background image download file and link URL 
        background_image_name = f"{radar_id}.background.png"

        # Full path to the background image file
        background_image_path = os.path.join(os.getcwd(), background_image_name)  

        # Check if the background image file already exists
        if not os.path.exists(background_image_path):
            background_image_url = f"{BACKGROUND_URL}/{background_image_name}"
            download_file(background_image_url, background_image_name)

        # Responsible for downloading the range map
        rangemap_name = f"{radar_id}.range.png"

        # full path to the rangemap file
        rangemap_path = os.path.join(os.getcwd(), rangemap_name)  

        # Check if the rangemap file already exists
        if not os.path.exists(rangemap_path):
            rangemap_url = f"{BACKGROUND_URL}/{rangemap_name}"
            log_event_db("ViewImage", f"Viewing image {rangemap_name}")
            download_file(rangemap_url, rangemap_name)

        # Responsible for downloading the legend image 
        legend_name = f"IDR.legend.1.png"
        legend_name_path = os.path.join(os.getcwd(), legend_name)
        if not os.path.exists(legend_name_path):
            legend_url = f"{BACKGROUND_URL}/{legend_name}"
            log_event_db("ViewImage", f"Viewing image {legend_name}") 
            download_file(legend_url, legend_name)

        # Responsible for downloading the legend wind image and checking if path exist
        wind_legend = f"IDR.legend.2.png"
        wind_legend_path = os.path.join(os.getcwd(), wind_legend)

        if not os.path.exists(wind_legend_path):
            wind_url = f"{BACKGROUND_URL}/{wind_legend}"
            log_event_db("ViewImage", f"Viewing image {wind_legend}")
            download_file(wind_url, wind_legend)

        # Cities for downloading image 
        cities_location_image = f"{radar_id}.locations.png"
        cities_location_path = os.path.join(os.getcwd(), cities_location_image)

        # Check if cities_location_image already exists 
        if not os.path.exists(cities_location_path):
            cities_location_url = f"{BACKGROUND_URL}/{cities_location_image}"
            log_event_db("ViewImage", f"Viewing image {cities_location_image}")
            download_file(cities_location_url, cities_location_image)

        # Find the images
        background_image = tk.PhotoImage(file=background_image_path)
        radar_image = tk.PhotoImage(file=image_path)
        range_image = tk.PhotoImage(file=rangemap_path)
        legend_image = tk.PhotoImage(file=legend_name_path)
        location_image = tk.PhotoImage(file=cities_location_path)


        # Create the images
        combined_canvas.create_image(0, 0, anchor=tk.NW, image=background_image)
        combined_canvas.create_image(0, 0, anchor=tk.NW, image=radar_image)
        combined_canvas.create_image(0, 0, anchor=tk.NW, image=range_image)
        combined_canvas.create_image(0, 0, anchor=tk.NW, image=legend_image)
        combined_canvas.create_image(0, 0, anchor=tk.NW, image=location_image)

        # Assigning image objects to attributes will prevent images from disappearing
        # in the canvas
        combined_canvas.background_image = background_image
        combined_canvas.radar_image = radar_image
        combined_canvas.range_image = range_image
        combined_canvas.legend_image = legend_image
        combined_canvas.location_image = location_image



def closing_interface() -> None:
    '''
    Close the program and records the application

    '''
    log_event_db("CloseProgram", "The application has been closed.")
    print('Closing the program Horayy')
    weather_interface.destroy()

def openning_database() -> list:
    """
    Connect to the database, fetch radar information, populate the Treeview 
    and return the radar information as a list of tuples.

    Returns:
    list: A list of tuples where each tuple contains (RadarId, RadarName).
    """

    connection = connect(DATABASE_NAME)
    cursor = connection.cursor()
    cursor.execute(SELECT_RADAR_INFO)
    radar_info = cursor.fetchall()
    
    # Iterate over radar_info and insert each radar into the table
    for radar in radar_info:
        table.insert("", tk.END, values=(radar[0], radar[1]))
    
    # Functions are used to download two text files
    download_radar_url()
    download_radar_transparencies_url()

    connection.close()
    
    # Return the list of tuples
    return radar_info


#<-------------------------------------------------------------------------------------------------------------------------------------------------------

# logs the event to database
log_event_db("OpenProgram", "The application has started.")
print("the application has open lol")

# Tkinter weather interface 
weather_interface = tk.Tk()
weather_interface.title("RainyDaze Weather App")


# Adjustments with the screen
screen_width = weather_interface.winfo_screenwidth()
screen_height = weather_interface.winfo_screenheight()
weather_interface.geometry(f"{screen_width}x{screen_height}")


# tkinter label 
application_label = tk.Label(weather_interface, text="RainyDaze (TM) Rain Radar Browser", font=("Helvetica", 16))
application_label.grid(row=0, column=1, pady=10)

frame = ttk.Frame(weather_interface)
frame.grid(row=1, column=0, padx=10, pady=10, sticky="nswe")

scrollbar = ttk.Scrollbar(frame, orient="vertical")

#displaying the radar stations table
columns = ("Radar ID", "Radar Name")
table = ttk.Treeview(frame, columns=columns, show="headings", yscrollcommand=scrollbar.set, height= 30)
print(f"{table}, i can see the table horray ")
for col in columns:
    table.heading(col, text=col)

table.column("Radar ID", width=270, stretch=tk.YES)
table.column("Radar Name", width=270, stretch=tk.YES)

scrollbar.config(command=table.yview)
scrollbar.pack(side="right", fill="y")

table.pack(side="left", fill="both", expand=True)


table.bind("<<TreeviewSelect>>", radar_station_select)

frame2 = ttk.Frame(weather_interface)
frame2.grid(row=1, column=1, padx=10, pady=10, sticky="nswe")


scrollbar2 = ttk.Scrollbar(frame2, orient="vertical")

# display the radar_weather_table 
columns2 = ("Radar ID", "Date", "Time")
table2 = ttk.Treeview(frame2, columns=columns2, show="headings", yscrollcommand=scrollbar2.set, height = 30)
print(table2)

for col in columns2:
    table2.heading(col, text=col)

table2.column("Radar ID", width=250, stretch=tk.YES)
table2.column("Date", width=250, stretch=tk.YES)
table2.column("Time", width=250, stretch=tk.YES)

scrollbar2.config(command=table2.yview)
scrollbar2.pack(side="right", fill="y")

# Create a custom style for the table
style = ttk.Style()


# Use the default theme
style.theme_use("default")  

# Define style for the table's heading
style.configure("Table.Heading", font=("Helvetica", 12), foreground="black", background="lightgrey")

# Define style for the table's rows
style.configure("Treeview", font=("Helvetica", 10), background="white", foreground="black", rowheight=25)
style.map("Treeview", background=[("selected", "grey")])

# Define style for the scrollbar
style.configure("Vertical.TScrollbar", background="lightgrey", bordercolor="grey")

# Apply the style to the table
table.config(style="Treeview")

table2.pack(side="left", fill="both", expand=True)

table2.bind("<<TreeviewSelect>>", radar_image_display)

combined_canvas = tk.Canvas(weather_interface, width=RADAR_IMAGE_WIDTH , height=RADAR_IMAGE_HEIGHT, relief="solid", borderwidth=2)
print(f"{combined_canvas}, canvas work yippe")
combined_canvas.grid(row=1, column=2, padx=10, pady=10)

btn_display_log = tk.Button(weather_interface, font = ('Arial', 10) ,text="Display Event Log", command= display_weather_report, width=20)
btn_display_log.grid(row=2, column= 1)

#call the function and capture the returned list and open DB
radar_info_list = openning_database()


weather_interface.protocol("WM_DELETE_WINDOW", closing_interface)

weather_interface.mainloop()

