#!/usr/bin/env python
from __future__ import print_function
import os
import feedparser
import re
import random
import sys
from BeautifulSoup import BeautifulSoup
import urllib2
import yagmail
import time

#ADD CREDENTIALS TO THE my_credentials.py file
import my_credentials as CREDS

#####################################################################################################################
# Scans the TALPodcast Feed for new episodes.
# Will download new episode or random episode based on user selection
# Episode temporarily stores on hard drive and then emails to specified email
#####################################################################################################################

#TO:DO - Get rid of repetitive functions and build generic emailer function (busy with finals, haven't coded yet)

#Email of your Gmail account to establish a valid SMTP connection with Gmail Servers
GMAIL_USER = CREDS.american_life_username

#Password of your Gmail account to establish a valid SMTP connection with Gmail Servers
GMAIL_PASSWORD = CREDS.american_life_password

#This is the person that will receive all of the mp3 files
RECIPIENT_USER_EMAIL = CREDS.american_life_recipient

#Folder the podcasts will reside in temporarily
#This will create if it does not exist
TEMP_POD_FOLDER = CREDS.american_life_podcast_directory_name

#Don't change this unless you know what you're doing
DESKTOP_FOLDER = os.getcwd()


#Parses the web for the latest podcast generated by Ira Glass
def retrieve_max_podcast_count():
    try:
        web_page = urllib2.urlopen("http://www.thisamericanlife.org/radio-archives").read()
        soup = BeautifulSoup(web_page)
        data = soup.findAll('div',attrs={'class':'episode-archive clearfix'});
        linker = None
        for div in data:
            linker = div.find('h3')
            break

        max_episode_count = re.search('(\d+[1-4])', "%s"%(linker))
        return max_episode_count.group(0)

    except urllib2.HTTPError:
        print("HTTPERROR!")
    except urllib2.URLError:
        print("URLERROR!")

def call_query_string(max_number):
    print("Querying random podcast from a list of %d potential TAL podcasts...\n"%(max_number))

def retrieve_random(max_number, repeat_query_string):

    if (repeat_query_string == 1):
        call_query_string(max_number)

    #Get a random podcast episode
    random_podcast_episode = random.randint(1, max_number)

    #Query first random url
    base_redirect_url = 'http://audio.thisamericanlife.org/jomamashouse/ismymamashouse/%d.mp3' %(random_podcast_episode)

    #Whether or not to continue (hitting enter will query a different episode)
    user_response = raw_input("Would you like to download This American Life Episode: %d? y/n/quit: "%(random_podcast_episode))

    if (user_response == "y"):
        os.system('''
        echo ""
        echo ""
        echo "*****************************************************"
        echo "CHECKING RANDOM VERSION OF TAL....."
        echo "RANDOM VERSION FOUND..."
        echo "DOWNLOAD PODCAST..."
        echo "*****************************************************"
        echo ""
        echo ""
        ''')

        #DL file_name off base_url
        os.system('curl -O %s'%(base_redirect_url))

        if (not os.path.exists(TEMP_POD_FOLDER)):
            os.system("mkdir " + TEMP_POD_FOLDER)

        #Change this directory to match your user setup environment.
        #DL's to root dir of script and moves into folder of same dir with pre-formatted naming convention
        os.system("mv *.mp3 %s/%s/episode_%s_TAL.mp3"%(DESKTOP_FOLDER, TEMP_POD_FOLDER,  random_podcast_episode))

        print('''

        *********************************************************
        *                                                       *
              CURRENTLY COMPRESSING AUDIO FILE FOR SENDING
        *                                                       *
        **********************************************************

        ''')

        #Zip the file to attach
        os.system("lame --mp3input -m m --resample 24 %s/%s/episode_%s_TAL.mp3"%(DESKTOP_FOLDER, TEMP_POD_FOLDER,  random_podcast_episode))

        print('''

        **************************************************************
        *                                                            *
            EMAILING THIS AMERICAN LIFE EPISODE #%s, please wait!
        *                                                            *
        **************************************************************

        ''' %(random_podcast_episode))


        yag = yagmail.SMTP(GMAIL_USER, GMAIL_PASSWORD)
        contents = ['Your requested audio MP3 has been sent to you successfully! Please download the attached MP3 File',
                    'You can find an audio file attached.', '%s/%s/episode_%s_TAL.mp3.mp3'%(DESKTOP_FOLDER, TEMP_POD_FOLDER, random_podcast_episode)]
        yag.send(RECIPIENT_USER_EMAIL, 'This American Life Podcast Episode!', contents)
        os.system("rm -r %s/*.mp3"%(TEMP_POD_FOLDER))

        print('''

        **************************************************************
        *                                                            *
              EMAIL SENT AND DOWNLOAD DIRECTORY HAS BEEN CLEARED
        *                                                            *
        **************************************************************

        ''')

    #If user chooses to exit the system
    elif (user_response == "quit"):
        print("Exiting...")
        sys.exit()

    #User wants a different podcast
    else:
        retrieve_random(max_number, 0)


def retrieve_latest():
    #Open the TAL feed
    url = 'http://feeds.feedburner.com/talpodcast'

    #Parse the feed url
    d = feedparser.parse(url)

    #Query the title
    podcast_title = d['entries'][0]['title']

    #REGEX parse the number to dl from the site
    m = re.search('(\d+[1-4])', podcast_title)

    #MP3 URL generation
    recent_podcast_url = d['entries'][0]['media_content'][0]['url']

    #sub_numeral redirect url
    base_redirect_url = 'http://podcast.thisamericanlife.org/podcast//%s.mp3' %(m.group(0))

    #user console output
    os.system('''
    echo ""
    echo ""
    echo "*****************************************************"
    echo "CHECKING LATEST VERSION OF TAL....."
    echo "LATEST VERSION FOUND..."
    echo "DOWNLOAD PODCAST..."
    echo "*****************************************************"
    echo ""
    echo ""
    ''')

    #CURL DL the file from the web
    os.system('curl -O %s'%(base_redirect_url))

    #Change this directory to match your user setup environment.
    #DL's to root dir of script and moves into folder of same dir with pre-formatted naming convention

    if (not os.path.exists(TEMP_POD_FOLDER)):
        os.system("mkdir " + TEMP_POD_FOLDER)

    os.system("mv *.mp3 %s/episode_%s_TAL.mp3"%(TEMP_POD_FOLDER, m.group(0)))

    random_podcast_episode = m.group(0)

    #Change this directory to match your user setup environment.
    #DL's to root dir of script and moves into folder of same dir with pre-formatted naming convention
    os.system("mv *.mp3 %s/episode_%s_TAL.mp3"%(TEMP_POD_FOLDER, random_podcast_episode))

    print('''

    *********************************************************
    *                                                       *
          CURRENTLY COMPRESSING AUDIO FILE FOR SENDING
    *                                                       *
    **********************************************************

    ''')

    #Zip the file to attach
    os.system("lame --mp3input -m m --resample 24 %s/%s/episode_%s_TAL.mp3"%(DESKTOP_FOLDER, TEMP_POD_FOLDER,  random_podcast_episode))

    print('''

    **************************************************************
    *                                                            *
        EMAILING THIS AMERICAN LIFE EPISODE #%s, please wait!
    *                                                            *
    **************************************************************

    ''' %(random_podcast_episode))


    yag = yagmail.SMTP(GMAIL_USER, GMAIL_PASSWORD)
    contents = ['Your requested audio MP3 has been sent to you successfully! Please download the attached MP3 File',
                'You can find an audio file attached.', '%s/%s/episode_%s_TAL.mp3.mp3'%(DESKTOP_FOLDER, TEMP_POD_FOLDER,  random_podcast_episode)]
    yag.send(RECIPIENT_USER_EMAIL, 'This American Life Podcast Episode!', contents)
    os.system("rm -r %s/*.mp3" %(TEMP_POD_FOLDER))

    print('''

    **************************************************************
    *                                                            *
          EMAIL SENT AND DOWNLOAD DIRECTORY HAS BEEN CLEARED
    *                                                            *
    **************************************************************

    ''')

def retrieve_by_user_specified(episode, max_episode_count):

    if (episode > max_episode_count):
        print("Sorry, you cannot enter more than %d episodes"%(max_episode_count))
    else:
        #Get a random podcast episode
        user_podcast_search_string = episode

        #Query first random url
        base_redirect_url = 'http://audio.thisamericanlife.org/jomamashouse/ismymamashouse/%d.mp3' %(user_podcast_search_string)

        #Whether or not to continue (hitting enter will query a different episode)
        user_response = raw_input("Would you like to download This American Life Episode: %d? y/n/quit: "%(user_podcast_search_string))

        if (user_response == "y"):
            os.system('''
            echo ""
            echo ""
            echo "*****************************************************"
            echo "CHECKING RANDOM VERSION OF TAL....."
            echo "RANDOM VERSION FOUND..."
            echo "DOWNLOAD PODCAST..."
            echo "*****************************************************"
            echo ""
            echo ""
            ''')

            #DL file_name off base_url
            os.system('curl -O %s'%(base_redirect_url))

            if (not os.path.exists(TEMP_POD_FOLDER)):
                os.system("mkdir " + TEMP_POD_FOLDER)

            #Change this directory to match your user setup environment.
            #DL's to root dir of script and moves into folder of same dir with pre-formatted naming convention
            os.system("mv *.mp3 %s/%s/episode_%s_TAL.mp3"%(DESKTOP_FOLDER, TEMP_POD_FOLDER, user_podcast_search_string))

            print('''

            *********************************************************
            *                                                       *
                  CURRENTLY COMPRESSING AUDIO FILE FOR SENDING
            *                                                       *
            **********************************************************

            ''')

            #Zip the file to attach
            os.system("lame --mp3input -m m --resample 24 %s/%s/episode_%s_TAL.mp3"%(DESKTOP_FOLDER, TEMP_POD_FOLDER, user_podcast_search_string))

            print('''

            **************************************************************
            *                                                            *
                EMAILING THIS AMERICAN LIFE EPISODE #%s, please wait!
            *                                                            *
            **************************************************************

            ''' %(user_podcast_search_string))


            yag = yagmail.SMTP(GMAIL_USER, GMAIL_PASSWORD)
            contents = ['Your requested audio MP3 has been sent to you successfully! Please download the attached MP3 File',
                        'You can find an audio file attached.', '%s/%s/episode_%s_TAL.mp3.mp3'%(DESKTOP_FOLDER, TEMP_POD_FOLDER, user_podcast_search_string)]
            yag.send(RECIPIENT_USER_EMAIL, 'This American Life Podcast Episode!', contents)
            os.system("rm -r %s/*.mp3"%(TEMP_POD_FOLDER))

            print('''

            **************************************************************
            *                                                            *
                  EMAIL SENT AND DOWNLOAD DIRECTORY HAS BEEN CLEARED
            *                                                            *
            **************************************************************

            ''')

        #If user chooses to exit the system
        elif (user_response == "quit"):
            print("Exiting...")
            sys.exit()

        elif (user_response == "n"):
            new_episode = raw_input("Please enter the new episode:  ")
            new_episode = int(new_episode)
            retrieve_by_user_specified(new_episode, max_episode_count)



#Main to execute following functions above
def main():

    print('''

**********************************************************************************************************
 _____ _     _        ___                      _                   _     _  __
|_   _| |   (_)      / _ \                    (_)                 | |   (_)/ _|
  | | | |__  _ ___  / /_\ \_ __ ___   ___ _ __ _  ___ __ _ _ __   | |    _| |_ ___
  | | | '_ \| / __| |  _  | '_ ` _ \ / _ \ '__| |/ __/ _` | '_ \  | |   | |  _/ _
  | | | | | | \__ \ | | | | | | | | |  __/ |  | | (_| (_| | | | | | |___| | ||  __/
  \_/ |_| |_|_|___/ \_| |_/_| |_| |_|\___|_|  |_|\___\__,_|_| |_| \_____/_|_| \___|

______         _               _    ______                    _                 _   _____           _
| ___ \       | |             | |   |  _  \                  | |               | | |_   _|         | |
| |_/ /__   __| | ___ __ _ ___| |_  | | | |_____      ___ __ | | ___   __ _  __| |   | | ___   ___ | |
|  __/ _ \ / _` |/ __/ _` / __| __| | | | / _ \ \ /\ / / '_ \| |/ _ \ / _` |/ _` |   | |/ _ \ / _ \| |
| | | (_) | (_| | (_| (_| \__ \ |_  | |/ / (_) \ V  V /| | | | | (_) | (_| | (_| |   | | (_) | (_) | |
\_|  \___/ \__,_|\___\__,_|___/\__| |___/ \___/ \_/\_/ |_| |_|_|\___/ \__,_|\__,_|   \_/\___/ \___/|_|

**********************************************************************************************************
                                    - Coded By Schachte -
**********************************************************************************************************

    ''')

    #Load up web call for max episode count
    print("Please wait, loading total This American Life Podcast Archive", end = '')
    sys.stdout.flush()

    #query the most recent episode
    max_episode_count = retrieve_max_podcast_count()

    #Ensure you're flushing out all chars from the buffer
    print("\rAll Podcasts Loaded....Please Continue                                                    \n\n")
    sys.stdout.flush()

    user_choice = raw_input("Would you like to:\n(1) Retrieve Most Recent Podcast\n(2) Retrieve Random Podcast\n(3) Enter User-Specified Episode Number\n(4) Quit\n")

    #Download the most recent TAL episode
    if (user_choice == "1"):
        retrieve_latest()

    #Download a random episode
    elif (user_choice == "2"):

        #Retrieve a random episode from the website
        retrieve_random(int(max_episode_count), 1)

    #Search by a user specified number
    elif (user_choice == "3"):
        user_episode_search = raw_input("What episode would you like to download of This American Life?:   ")
        retrieve_by_user_specified(int(user_episode_search), int(max_episode_count))
        #exit program
    elif (user_choice == "4"):
            sys.exit()
    else:
        print("Invalid..\n")

if __name__ == "__main__":
    main()
