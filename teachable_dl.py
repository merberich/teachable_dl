#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import json

import wget
import requests
import lxml.html

from http.cookiejar import MozillaCookieJar
from bs4 import BeautifulSoup
from slugify import slugify
import youtube_dl

import argparse

class TeachableDownloader():
  def __init__(self, cookies_file=None, courses_list=None, out_dir=None):
    self.sess = requests.session()
    self.cookies_file = cookies_file
    self.courses_list = courses_list
    self.out_dir = out_dir

  def run(self):
    """Performs a full download of all requested courses after instantiation."""
    if self.cookies_file == None:
      print("No cookies file provided.")
      return
    elif not os.path.isfile(self.cookies_file):
      print("Could not find or load cookies file.")
      return

    if self.courses_list == None or (isinstance(self.courses_list, list) and len(self.courses_list) == 0):
      print("No course URLs provided.")
      return

    if self.out_dir != None and not os.path.isdir(self.out_dir):
      print("Invalid output directory.")
      return

    try:
      self._load_cookies()
    except Exception as e:
      print("Error loading cookies file: " + str(e))
      return
    for course_url in self.courses_list:
      try:
        self._fetch_course(course_url)
      except Exception as e:
        print("Failed to download course materials at URL: " + course_url + ". Cause: " + str(e))

  def _load_cookies(self):
    """Attempts to load cookies into current requests session."""
    cj = MozillaCookieJar()
    cj.load(self.cookies_file)
    self.sess.cookies.update(cj)

  def _fetch_course(self, course_url):
    """Attempts to download all relevant information for a course."""
    print("Fetching course url: '" + course_url + "'")

    course_info = self._get_course_info(course_url)
    self._download_course(course_url, course_info)
    # @todo continue

  def _get_course_info(self, course_url):
    """"Identifies course title and relevant course sections."""
    response = self.sess.get(course_url)
    if response.ok:
      homepage_html = BeautifulSoup(response.text, "html.parser")
      course_title = self._parse_course_title(homepage_html)
      if course_title == None:
        return None
      course_sections_list = self._parse_course_sections(homepage_html)
      if len(course_sections_list) == 0:
        return None
      return {"title": course_title, "sections": course_sections_list}
    else:
      print("Failed to grab course info at URL: " + course_url + ". Cause: " + response.reason)
      return None

  def _parse_course_title(self, homepage_html):
    """Identifies course title within homepage HTML."""
    sidebar_html = homepage_html.find("div", attrs={"class": "course-sidebar"})
    if sidebar_html == None:
      print("Not signed into course (via cookies).")
      return None
    course_title_html = sidebar_html.find("h2")
    if course_title_html == None:
      print("Unexpected page format (has teachable reworked their frontend?)")
      return None
    return slugify(str(course_title_html.get_text()).strip())

  def _parse_course_sections(self, homepage_html):
    """Identifies course sections, decomposed by title and lesson links."""
    sec_html_list = homepage_html.find_all(class_="course-section")
    if sec_html_list == None:
      print("Failed to find course sections (has teachable reworked their frontend?)")
      return None
    sections = list()
    for sec_html in sec_html_list:
      sec_title = self._parse_section_title(sec_html)
      sec_lessons_list = self._parse_section_lessons(sec_html)
      if sec_title == None or sec_lessons_list == None or len(sec_lessons_list) == 0:
        print("Failed to scrape section (has teachable reworked their frontend?)")
      else:
        sections.append({"title": sec_title, "lessons": sec_lessons_list})
    return sections

  def _parse_section_title(self, sec_html):
    """Identifies section title within section HTML."""
    sec_title_html = sec_html.find("div", attrs={"class": "section-title"})
    if sec_title_html == None:
      print("Section title not found.")
      return None
    return slugify(str(sec_title_html.contents[2]).strip())

  def _parse_section_lessons(self, sec_html):
    """Identifies lessons associated with section HTML, by title and link."""
    lesson_html_list = sec_html.find_all("a", class_="item")
    lessons = list()
    for lesson_html in lesson_html_list:
      lesson_title = self._parse_lesson_title(lesson_html)
      lesson_rel_link = self._parse_lesson_rel_link(lesson_html)
      if lesson_title == None or lesson_rel_link == None:
        print("Failed to scrape lesson (has teachable reworked their frontend?)")
      else:
        lessons.append({"title": lesson_title, "rel_link": lesson_rel_link})
    return lessons

  def _parse_lesson_title(self, lesson_html):
    """Identifies lesson title associated with lesson block HTML."""
    lesson_title_html = lesson_html.find("span", attrs={"class": "lecture-name"})
    if lesson_title_html == None:
      print("Lesson title not found.")
      return None
    return slugify(str(lesson_title_html.get_text()).strip())

  def _parse_lesson_rel_link(self, lesson_html):
    """Identifies lesson link associated with lesson block HTML."""
    return lesson_html.attrs["href"]

  def _download_course(self, course_url, course_info):
    """Downloads all resources associated with the course."""
    root_path = os.path.abspath(self.out_dir or os.getcwd())
    root_url = course_url.split("/courses")[0]

    # Prep class directory
    class_path = os.path.join(root_path, course_info["title"])
    os.makedirs(class_path, exist_ok = True)

    # Prep section directories and work within them
    for idx, section in enumerate(course_info["sections"]):
      section_path = os.path.join(class_path, str(idx) + "_" + section["title"])
      os.makedirs(section_path, exist_ok = True)

      # Prep lesson directories and work within them
      for idx, lesson in enumerate(section["lessons"]):
        lesson_path = os.path.join(section_path, str(idx) + "_" + lesson["title"])
        lesson_url = root_url + lesson["rel_link"]
        os.makedirs(lesson_path, exist_ok = True)

        try:
          self._download_lesson(lesson["title"], lesson_url, lesson_path)
        except Exception as e:
          print("Failed to download lesson: " + lesson["title"] + ", cause: " + str(e))

  def _download_lesson(self, title, url, output_path):
    """Downloads a single lesson as HTML and any associated media."""
    response = self.sess.get(url)
    if response.ok:
      # Properly handle video attachments
      lesson_html = BeautifulSoup(response.text, "html.parser")
      video_html_list = lesson_html.find_all(class_="lecture-attachment-type-video")
      for idx, video_html in enumerate(video_html_list):
        # Reserve a new video element in the HTML for a plain MP4
        vidname = title + "_" + str(idx) + ".mp4"
        video_tag_new = lesson_html.new_tag("video",
          id = video_html.id,
          src = vidname,
          type = "video/mp4",
          autoplay = "",
          preload="auto",
          controls="",
          style="max-width: 75%; margin: 0px auto; display: block;"
        )
        video_html.insert_before(video_tag_new)

        # Download the video to the appropriate location
        wistia_html = video_html.find("div", attrs={"class": "attachment-wistia-player"})
        wistia_id = wistia_html.get("data-wistia-id")
        ydl_opts = {
          "format": "mp4",
          "outtmpl": os.path.join(output_path, vidname),
          "quiet": True
        }
        try:
          with youtube_dl.YoutubeDL(ydl_opts) as ydl:
              ydl.download(["http://fast.wistia.net/embed/iframe/" + str(wistia_id)])
        except Exception as e:
          print("Could not download " + vidname + ", cause: " + str(e))

        # Remove the original video tag from the HTML
        video_html.decompose()

      # Remove comments section for portability + security
      comments_html = lesson_html.find("div", attrs={"class": "comments"})
      if comments_html != None:
        comments_html.decompose()

      # Postprocess images
      image_html_list = lesson_html.find_all("img")
      for idx, image_html in enumerate(image_html_list):
        # Ensure images fit the HTML render area
        existing_style = ""
        new_style = "max-width: 75%; margin: 0px auto; display: block;"
        if "style" in image_html.attrs:
          existing_style = image_html.attrs["style"]
        image_html.attrs.update({"style": existing_style + new_style})
        # Bypass image loading scripts
        for k,v in image_html.attrs.items():
          if k == "src":
            break
          if "src" in k:
            image_html.attrs.update({"src": v})
            break

      # Save the lesson HTML after reformatting
      lesson_content_html = lesson_html.find("div", attrs={"class": "lecture-content"})
      lecture_filename = os.path.join(output_path, title + ".html")
      with open(lecture_filename, "w+", encoding = "utf-8") as file:
        file.write(lesson_content_html.prettify())
    else:
      print("Failed to grab lesson " + title)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description = "Teach:Able content downloader.")
  parser.add_argument("-c", "--cookies",
    required = True,
    help = "Cookies file containing logged-in session for the desired course(s)."
  )
  parser.add_argument("-u", "--url",
    default = None,
    nargs = "+",
    help = "List of URLs of courses to download."
  )
  parser.add_argument("-o", "--output",
    default = None,
    help = "Output directory in which to place downloaded course content."
  )
  args = parser.parse_args(sys.argv[1:])

  try:
    TeachableDownloader(
      cookies_file = args.cookies,
      courses_list = args.url,
      out_dir = args.output
    ).run()
  except KeyboardInterrupt:
    print("User Interrupted.")
    sys.exit(1)
  except Exception as e:
    print("Error occurred: " + str(e))
