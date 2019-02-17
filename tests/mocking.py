class MockBranch(object):
    def __init__(self, name):
        self.name = name


class MockRepo(object):
    def __init__(self, active_branch_name):
        self.active_branch_name = active_branch_name

    @property
    def active_branch(self):
        return MockBranch(self.active_branch_name)
