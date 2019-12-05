import goless
from goless import waitgroup
from . import BaseTests


class WaitGroupTests(BaseTests):
    def test_blocks_for_done(self):
        wg = goless.WaitGroup(10)
        wg.add(5)

        counter = [0]

        def callback():
            counter[0] += 1
            wg.done()

        for _ in range(15):
            goless.go(callback)

        wg.wait()
        self.assertEqual(counter[0], 15)

    def test_done_before_wait_does_not_block(self):
        wg = goless.WaitGroup(1)
        wg.done()
        wg.wait()

    def test_can_select(self):
        pass

    def test_errors_on_non_positive_add(self):
        with self.assertRaisesRegex(waitgroup.InvalidWaitGroup, 'add delta must be positive'):
            goless.WaitGroup(-1)

    def test_errors_on_unbalanced_done(self):
        wg = goless.WaitGroup()
        with self.assertRaisesRegex(waitgroup.InvalidWaitGroup, 'done called for a task that was never added'):
            wg.done()

    def test_errors_on_multiple_wait(self):
        wg = goless.WaitGroup()
        wg.wait()
        with self.assertRaisesRegex(waitgroup.InvalidWaitGroup, 'wait can only be called once'):
            wg.wait()

    def test_add_after_wait_errors(self):
        wg = goless.WaitGroup()
        wg.wait()
        with self.assertRaisesRegex(waitgroup.InvalidWaitGroup, 'add cannot be called after wait'):
            wg.add(1)
