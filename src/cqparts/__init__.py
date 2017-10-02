import sys
import logging

# --- Initialize logging
root = logging.getLogger()
root.setLevel(logging.INFO)

# FreeCAD Logging Handler
class FreeCADConsoleHandler(logging.Handler):
    # Custom flag to identify loggers writing to the FreeCAD.Console
    # why?, This same implementation may appear in cadquery, this helps
    # avoid duplicate logging for the overlapping versions of cadquery and cqparts
    freecad_console = True

    def emit(self, record):
        log_text = self.format(record) + "\n"
        if record.levelno >= logging.ERROR:
            FreeCAD.Console.PrintError(log_text)
        elif record.levelno >= logging.WARNING:
            FreeCAD.Console.PrintWarning(log_text)
        else:
            FreeCAD.Console.PrintMessage(log_text)

try:
    import cadquery # necessary to import FreeCAD
    import FreeCAD
    FreeCAD.Console  # will raise exception if not available

    freecad_handler = FreeCADConsoleHandler()
    freecad_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(message)s')
    freecad_handler.setFormatter(formatter)

    if not any(getattr(h, 'freecad_console', False) for h in root.handlers):
        # to avoid duplicate logging
        root.addHandler(freecad_handler)

except Exception as e:
    # Fall back to STDOUT output (better than nothing)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(message)s')
    stdout_handler.setFormatter(formatter)
    root.addHandler(stdout_handler)
