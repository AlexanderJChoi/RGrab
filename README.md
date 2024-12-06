# RGrab
Python Gui application that downloads all comments from a reddit thread into a file.

## Dependencies
- [PRAW 7.7.1](https://praw.readthedocs.io/en/stable/index.html)
- [Qt for Python 6.8](https://doc.qt.io/qtforpython-6/index.html)

## Setup
 - Obtain a client secret and client id for interacting with Reddit's API. This can be done by signing into a Reddit account, then following the instructions on the [Reddit OAuth2 First Steps Guide](https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example#first-steps)
 - Create a user agent to identify your application. Guidance on this can be found on the [Reddit API Wiki Rules section](https://github.com/reddit-archive/reddit/wiki/API#rules)
 - Copy and paste each of these, respectively, into files named `.client_secret`, `.client_id`, and `.user_agent` in the RGrab folder.
