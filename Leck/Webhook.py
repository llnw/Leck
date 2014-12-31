#!/usr/bin/env python
# Simple webhook to recieve a payload from GitHub and fire validation / review
#  logic for pull/peer review comments section.

import web
import PullCheck

app = web.application(('/.*', 'hooks'), globals())


class hooks:
    def POST(self):
        PullCheck.LeckPullChecker.create_pullcheck_from_hook(
            web.ctx.env.get('HTTP_X_GITHUB_EVENT'),
            web.data())
        return 'OK'  # TODO: put some logging in the return message...

if __name__ == '__main__':
    app.run()
