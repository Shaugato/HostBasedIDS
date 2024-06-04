import unittest
from unittest.mock import patch
from HIDS.utils.synchronous_interval_scheduler import SynchronousIntervalScheduler

class TestSynchronousIntervalScheduler(unittest.TestCase):
    @patch('HIDS.utils.synchronous_interval_scheduler.SynchronousIntervalScheduler.run_once')
    def test_run_forever(self, mock_run_once):
        scheduler = SynchronousIntervalScheduler(lambda: None, interval=1)
        scheduler.run_forever()
        mock_run_once.assert_called()

if __name__ == '__main__':
    unittest.main()
