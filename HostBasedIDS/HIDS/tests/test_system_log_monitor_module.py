import unittest
from unittest.mock import patch, call
from HIDS.utils.synchronous_interval_scheduler import SynchronousIntervalScheduler

class TestSynchronousIntervalScheduler(unittest.TestCase):
    def test_run_forever(self):
        mock_task = patch('HIDS.utils.synchronous_interval_scheduler.task').start()
        scheduler = SynchronousIntervalScheduler(mock_task, interval=1)
        with patch.object(scheduler, 'stop_event', side_effect=[False, False, True]):
            scheduler.run_forever()
        self.assertEqual(mock_task.call_count, 2)

if __name__ == '__main__':
    unittest.main()

