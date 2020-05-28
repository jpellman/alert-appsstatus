import unittest
from alert_appsstatus import compareStatus

class TestCompareStatus(unittest.TestCase):

    def test_statechange_noprevious_gmailonly(self):
        with open("examples/2014-11-25.xml","r") as f:
            currentStatus = "".join(f.readlines())
        alerts = compareStatus(currentStatus,"examples/null.xml","statechange",["Gmail"],False)
        for alert in alerts:
            self.assertTrue(alert.title in ["Gmail"])
        self.assertTrue(len(alerts) == 1)

    def test_statechange_previous_gmailonly(self):
        with open("examples/2014-11-25.xml","r") as f:
            currentStatus = "".join(f.readlines())
        alerts = compareStatus(currentStatus,"examples/normal.xml","statechange",["Gmail"],False)
        for alert in alerts:
            self.assertTrue(alert.title in ["Gmail"])
        self.assertTrue(len(alerts) == 1)

    def test_continuous_previous_gmailonly(self):
        with open("examples/2014-11-25.xml","r") as f:
            currentStatus = "".join(f.readlines())
        alerts = compareStatus(currentStatus,"examples/normal.xml","continuous",["Gmail"],False)
        for alert in alerts:
            self.assertTrue(alert.title in ["Gmail"])
        self.assertTrue(len(alerts) == 1)

    def test_continuous_nochange_gmailonly(self):
        with open("examples/2014-11-25.xml","r") as f:
            currentStatus = "".join(f.readlines())
        alerts = compareStatus(currentStatus,"examples/2014-11-25.xml","continuous",["Gmail"],False)
        for alert in alerts:
            self.assertTrue(alert.title in ["Gmail"])
        self.assertTrue(len(alerts) == 1)

    def test_statechange_noprevious_gmailmultiple(self):
        with open("examples/2020-04-08.xml","r") as f:
            currentStatus = "".join(f.readlines())
        alerts = compareStatus(currentStatus,"examples/null.xml","statechange",["Gmail"],False)
        for alert in alerts:
            self.assertTrue(alert.title in ["Gmail"])
        self.assertTrue(len(alerts) == 3)

    def test_statechange_previous_gmailmultiple(self):
        with open("examples/2020-04-08.xml","r") as f:
            currentStatus = "".join(f.readlines())
        alerts = compareStatus(currentStatus,"examples/normal.xml","statechange",["Gmail"],False)
        for alert in alerts:
            self.assertTrue(alert.title in ["Gmail"])
        self.assertTrue(len(alerts) == 3)

    def test_continuous_previous_gmailmultiple(self):
        with open("examples/2020-04-08.xml","r") as f:
            currentStatus = "".join(f.readlines())
        alerts = compareStatus(currentStatus,"examples/normal.xml","continuous",["Gmail"],False)
        for alert in alerts:
            self.assertTrue(alert.title in ["Gmail"])
        self.assertTrue(len(alerts) == 3)

    def test_statechange_noprevious_gmailblacklist(self):
        with open("examples/2020-04-08.xml","r") as f:
            currentStatus = "".join(f.readlines())
        alerts = compareStatus(currentStatus,"examples/null.xml","statechange",["Gmail"],True)
        self.assertTrue(len(alerts) == 0)

    def test_statechange_previous_gmailblacklist(self):
        with open("examples/2020-04-08.xml","r") as f:
            currentStatus = "".join(f.readlines())
        alerts = compareStatus(currentStatus,"examples/normal.xml","statechange",["Gmail"],True)
        self.assertTrue(len(alerts) == 0)

    def test_continuous_previous_gmailblacklist(self):
        with open("examples/2020-04-08.xml","r") as f:
            currentStatus = "".join(f.readlines())
        alerts = compareStatus(currentStatus,"examples/normal.xml","continuous",["Gmail"],True)
        self.assertTrue(len(alerts) == 0)

    def test_whitelist_many_services(self):
        with open("examples/2020-03-04.xml","r") as f:
            currentStatus = "".join(f.readlines())
        whitelist = ["Google Sheets","Google Sites"]
        alerts = compareStatus(currentStatus,"examples/normal.xml","continuous",whitelist ,False)
        for alert in alerts:
            self.assertTrue(alert.title in whitelist)
        self.assertTrue(len(alerts) == 9)

    def test_blacklist_many_services(self):
        with open("examples/2020-03-04.xml","r") as f:
            currentStatus = "".join(f.readlines())
        blacklist = ["Google Sheets","Google Sites"]
        alerts = compareStatus(currentStatus,"examples/normal.xml","continuous",blacklist ,True)
        for alert in alerts:
            self.assertTrue(alert.title not in blacklist)
        self.assertTrue(len(alerts) == 22)

if __name__ == '__main__':
    unittest.main()
