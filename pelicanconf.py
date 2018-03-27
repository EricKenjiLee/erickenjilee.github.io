#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Eric Kenji Lee'
SITENAME = "Kenji's Data Blog"
SITEURL = ''

PATH = 'content'
STATIC_PATHS = ['images']
ARTICLE_SAVE_AS = '{date:%Y}/{slug}.html'
ARTICLE_URL = '{date:%Y}/{slug}.html'

TIMEZONE = 'America/Los_Angeles'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),)

# Social widget
SOCIAL = (('LinkedIn', 'https://www.linkedin.com/in/erickenjilee/'),
          ('GitHub', 'https://github.com/EricKenjiLee/'),)

DEFAULT_PAGINATION = 10

DISQUS_SITENAME = "erickenjilee-com"
GOOGLE_ANALYTICS = "UA-116317987-1"
TWITTER_USERNAME = "EricKenjiLee"

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
