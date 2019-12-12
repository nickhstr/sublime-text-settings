# Copied from https://raw.githubusercontent.com/rodrigobdz/subl-gitblame-statusbar/master/git_blame_sublime_statusbar.py

import sublime
import sublime_plugin
import os
import subprocess
from subprocess import check_output as shell
from datetime import datetime
from math import floor
import re

try:
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
except:
    si = None


class GitBlameStatusbarCommand(sublime_plugin.EventListener):
    def parse_blame(self, blame):
        user_pattern = '[\w ]+(?=(\d{4}-\d{2}-\d{2}))'
        datetime_pattern = '\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        not_committed_pattern = 'Not Committed'

        user_match = re.search(user_pattern, blame)
        datetime_match = re.search(datetime_pattern, blame)
        not_committed_match = re.search(not_committed_pattern, blame)

        if user_match and datetime_match:
            user = user_match.group(0).strip()

            if not_committed_match:
                user = 'You'

            date = datetime_match.group(0).strip()
            return (user, date)

        return ('', '')

    def get_blame(self, line, path):
        try:
            return shell(["git", "blame", "--minimal", "-w",
                        "-L {0},{0}".format(line), path],
                        cwd=os.path.dirname(os.path.realpath(path)),
                        startupinfo=si,
                        stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            pass
            # print("Git blame: git error {}:\n{}".format(e.returncode, e.output.decode("UTF-8")))
        except Exception as e:
            pass
            # print("Git blame: Unexpected error:", e)

    def time_between(self, d):
        now = datetime.now()
        d = datetime.strptime(d, "%Y-%m-%d %H:%M:%S")
        delta = now - d

        years = round(abs(delta.days / 365))
        months = round(abs(delta.days / 30))
        days = abs(delta.days)
        hours = floor(abs(delta.seconds / 60 / 60))
        minutes = floor(abs(delta.seconds / 60))

        if years > 0:
            return "{0} {1} ago".format(years, 'years' if years > 1 else 'year')
        if months > 0:
            return "{0} {1} ago".format(months, 'months' if months > 1 else 'month')
        elif days > 0:
            return "{0} {1} ago".format(days, 'days' if days > 1 else 'day')
        elif hours > 0:
            return "{0} {1} ago".format(hours, 'hours' if hours > 1 else 'hour')
        elif minutes > 0:
            return "{0} {1} ago".format(minutes, 'minutes' if minutes > 1 else 'minute')

        return "a few seconds ago"

    def on_selection_modified_async(self, view):
        current_line = view.substr(view.line(view.sel()[0]))
        (row, col) = view.rowcol(view.sel()[0].begin())
        path = view.file_name()
        blame = self.get_blame(int(row) + 1, path)
        output = ''

        if blame:
            blame = blame.decode('utf-8')
            user, date = self.parse_blame(blame)
            time_since = self.time_between(date)
            output = user + ", " + time_since

        view.set_status('git_blame', output)