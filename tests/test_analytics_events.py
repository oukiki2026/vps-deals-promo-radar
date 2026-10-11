import pathlib
import shutil
import subprocess
import unittest


class AnalyticsEventsTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'), 'Node runtime unavailable')
    def test_consent_and_safe_click_events(self):
        script = pathlib.Path(__file__).with_suffix('.js')
        subprocess.run([shutil.which('node'), str(script)], check=True, capture_output=True)
