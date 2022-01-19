from addons.integromat.serializer import IntegromatSerializer

class IntegromatProvider(object):
    name = 'Integromat'
    short_name = 'integromat'
    serializer = IntegromatSerializer

    def __init__(self, account=None):
        super(IntegromatProvider, self).__init__()  # this does exactly nothing...
        # provide an unauthenticated session by default
        self.account = account

    def __repr__(self):
        return '<{name}: {status}>'.format(
            name=self.__class__.__name__,
            status=self.account.display_name if self.account else 'anonymous'
        )
