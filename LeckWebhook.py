#!/usr/bin/env python
# Simple webhook to recieve a payload from GitHub and fire validation / review
#  logic for pull/peer review comments section.

import web

urls = ('/.*', 'hooks')

app = web.application(urls, globals())


class hooks:
    def POST(self):
        data = web.data()
        print
        print 'UA'
        print web.ctx.env.get('HTTP_USER_AGENT')
        print 'Event'
        print web.ctx.env.get('HTTP_X_GITHUB_EVENT')
        print 'Delivery'
        print web.ctx.env.get('HTTP_X_GITHUB_DELIVERY')
        print 'DATA RECEIVED:'
        print data
        print
        return 'OK'

if __name__ == '__main__':
    app.run()
