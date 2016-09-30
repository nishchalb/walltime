#!/usr/bin/env python
import cv2
import numpy as np
import sqlite3
import peewee
from scipy.spatial.distance import euclidean
import datetime
import matplotlib as mpl
import matplotlib.cm as cm
import subprocess
from random import shuffle
import argparse
import glob
import os

db = peewee.SqliteDatabase(os.path.expanduser('~/.walltime/wall.db'))
# db = peewee.SqliteDatabase('wall.db')
db.connect()

# Define object for db
class Wallpaper(peewee.Model):
    name = peewee.CharField(primary_key=True)
    mean_l = peewee.DoubleField()
    mean_a = peewee.DoubleField()
    mean_b = peewee.DoubleField()

    class Meta:
        database = db

""" Convert a BGR image to LAB
"""
def lab(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

def mean_l(img):
    return np.mean(img[:,:,0])

def mean_a(img):
    return np.mean(img[:,:,1])

def mean_b(img):
    return np.mean(img[:,:,2])

""" Adds the image with the given filename to the database,
    including relevant statistics about it.

    Args:
      filename (string): the path of the file to add
"""
def add_img(filename):
    img = cv2.imread(filename)
    limg = lab(img)
    ml = mean_l(limg)
    ma = mean_a(limg)
    mb = mean_b(limg)
    Wallpaper.create(name=filename, mean_l=ml, mean_a=ma, mean_b=mb)

""" Given a list of filenames, make sure the DB includes them all

    Args:
      filenames (list): A list containing filepaths
"""
def update_db(filenames):
    for filename in filenames:
        if Wallpaper.select().where(Wallpaper.name == filename).count()<1:
            print 'Adding {} to the database'.format(filename)
            add_img(filename)

"""Returns the filename of the wallpaper in the DB that is the closest
    match to the given LAB color.

    Args:
      l (float): the value of the l channel to match
      a (float): the value of the a channel to match
      b (float): the value of the b channel to match

    Returns:
      string: The name of the file in the database that is the best match
"""
def best_match(l, a, b):
    best_name = ''
    best_dist = float('inf')
    for wallpaper in Wallpaper.select():
        color1 = np.asarray([l, a, b])
        color2 = np.asarray([wallpaper.mean_l, wallpaper.mean_a, wallpaper.mean_b])
        dist = euclidean(color1, color2)
        if dist < best_dist:
            best_dist = dist
            best_name = wallpaper.name
    return best_name

""" Return the top n matches to the given LAB color

    Args:
        l (float): the value of the l channel to match
        a (float): the value of the a channel to match
        b (float): the value of the b channel to match
        n (int): the number of matches to return

    Returns:
        list of (string, float): the filenames and distances of the matches
"""
def top_matches(l, a, b, n):
    matches = []
    for wallpaper in Wallpaper.select():
        color1 = np.asarray([l, a, b])
        color2 = np.asarray([wallpaper.mean_l, wallpaper.mean_a, wallpaper.mean_b])
        dist = euclidean(color1, color2)
        matches.append((wallpaper.name, dist))
    matches.sort(key=lambda t: t[1])
    return matches[:n]


""" Calculates a LAB color corresponding to a given time

    Args:
      time (datetime.datetime): the time to generate a color for

    Returns:
      numpy.ndarray: An array with shape (1,1,3) representing a single color
"""
def color_for_time(time):
    cmap = cm.get_cmap('viridis')
    hour = time.hour
    minute = time.minute
    total = hour*60+minute
    if total > 720:
      total = 1440 - total
    index = int(round(255*total/720.))
    color = np.asarray(cmap.colors[index])
    color = color.reshape((1,1,3))
    color *= 255
    color = color.astype('uint8')
    return cv2.cvtColor(color, cv2.COLOR_RGB2LAB)

def set_bg(filename):
  subprocess.call(['feh', '--bg-scale', filename])

def best_match_for_time(time):
  color = color_for_time(time)
  bm = best_match(color[0,0,0], color[0,0,1], color[0,0,2])
  return bm

def update_bg_reasonable_now():
    now = datetime.datetime.now()
    color = color_for_time(now)
    matches = top_matches(color[0,0,0], color[0,0,1], color[0,0,2], 10)
    thresh = matches[0][1]*1.10 #10% over smallest match
    reasonable_matches = filter(lambda t: t[1]<=thresh, matches)
    print reasonable_matches
    shuffle(reasonable_matches)
    set_bg(reasonable_matches[0][0])


def update_bg_best_now():
  now = datetime.datetime.now()
  best_bg = best_match_for_time(now)
  set_bg(best_bg)

def main():
    db.create_table(Wallpaper, True) # Create the table if it doesn't exist

    parser = argparse.ArgumentParser(
            description='''Select the most appropriate of your wallpapers based on
                         the current time of day''')
    parser.add_argument(
            '-u',
            '--update',
            help= '''Update the database of images with the given directory. A directory
            must be given. This will not change the wallpaper'''
            )
    parser.add_argument(
            '-b',
            '--best',
            help = '''Whether to use the best image or not. If this flag is used,
                    the best image will be selected. Otherwise, a reasonable one
                    will be used'''
            )

    args = parser.parse_args()

    if args.update:
        path = args.update
        filenames = glob.glob('{}*.jpg'.format(path)) + glob.glob('{}*.png'.format(path))
        abs_filenames = map(os.path.abspath, filenames)
        update_db(abs_filenames)
        return
    elif args.best:
        update_bg_best_now()
    else:
        update_bg_reasonable_now()

if __name__ == '__main__':
    main()

