# -*- coding: utf-8 -*-
from bottle import app, route, run, template, error
import server_func

app = app()

'''
error processing
'''
@error(404)
def error404(error):
    return 'no action found'

if __name__ ==  '__main__':
    run(app=app, host='0.0.0.0', port=18888)
