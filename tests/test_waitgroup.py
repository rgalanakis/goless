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

    def test_wait_case_returns_case_for_select_when_counter_is_zero(self):
        wg = goless.WaitGroup()
        wg.add(1)
        wg.done()

        wait_case = wg.wait_case()
        selected, _ = goless.select([wait_case, goless.dcase()])
        self.assertIs(selected, wait_case)

    def test_wait_case_returns_case_for_select_when_counter_is_positive(self):
        wg = goless.WaitGroup()
        wg.add(1)

        wait_case = wg.wait_case()
        selected, _ = goless.select([goless.dcase(), wait_case])
        self.assertIsNot(selected, wait_case)

        wg.done()
        selected, _ = goless.select([goless.dcase(), wait_case])
        self.assertIs(selected, wait_case)

    def test_wait_case_errors_if_already_waited(self):
        wg = goless.WaitGroup()
        wg.wait()
        with self.assertRaisesRegex(waitgroup.InvalidWaitGroup, 'wait can only be called once'):
            wg.wait_case()

    def test_wait_case_with_no_counter_selects(self):
        wg = goless.WaitGroup()
        wait_case = wg.wait_case()
        selected, _ = goless.select([goless.dcase(), wait_case])
        self.assertIs(selected, wait_case)
