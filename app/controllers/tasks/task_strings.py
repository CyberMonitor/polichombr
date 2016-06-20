import os
import re
import time

from app import app
from app.models.sample import StringsType
from app.controllers.task import Task
from app.controllers.sample import SampleController


class task_strings(Task):
    """
    Extract wide/ascii strings metadata form file using regexps.
    """

    def __init__(self, sample):
        super(task_strings, self).__init__()
        self.sid = sample.id
        self.fpath = sample.storage_file
        self.resultstrings = []
        self.execution_level = 0
        self.tmessage = "STRINGS TASK %d :: " % (self.sid)
        self.tstart = 0

    def execute(self):
        self.tstart = int(time.time())
        app.logger.debug(self.tmessage + "EXECUTE")
        if os.path.exists(self.fpath):
            try:
                data = open(self.fpath, "r").read()
            except (IOError, OSError) as e:
                app.logger.exception(e)
                return False
            asciistrings = re.findall("[\x1f-\x7e]{6,}", data)
            unicodestrings = [str(ws.decode("utf-16le"))
                              for ws in re.findall("(?:[\x1f-\x7e][\x00]){6,}",
                                                   data)]
            for s in asciistrings:
                tmp = (StringsType.ASCII, s)
                if tmp not in self.resultstrings:
                    self.resultstrings.append(tmp)
            for s in unicodestrings:
                tmp = (StringsType.UNICODE, s)
                if tmp not in self.resultstrings:
                    self.resultstrings.append(tmp)
        else:
            return False
        return True

    def apply_result(self):
        s_controller = SampleController()
        sample = s_controller.get_by_id(self.sid)
        app.logger.debug(self.tmessage + "APPLY_RESULT")
        s_controller.add_multiple_strings(sample, self.resultstrings)
        app.logger.debug(self.tmessage + "END - TIME %i" %
                         (int(time.time()) - self.tstart))
        return True
