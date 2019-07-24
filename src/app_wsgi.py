import cgi
import json

def application(environ, start_response):

    if environ['REQUEST_METHOD'] == 'POST':
        request_body_size = int(environ.get('CONTENT_LENGTH', '0'))
        request_body = environ['wsgi.input'].read(request_body_size)
        data = json.loads(request_body.decode())

        if data['state']:
            # The first command 'start' doesn't have any state
            game_logic.set_state(data['state'])

        prompts = game_logic.do_command(data['user_command'])

        text = ''
        audio = []
        for prompt in prompts:
            txt = prompt['text']
            if txt:
                if txt.endswith('^'):
                    txt = txt[0:-1]
                else:
                    txt = txt + '\n'
                text = text + txt
            audio.append(prompt['audio'])

        ndata = {
            'text': text,
            'audio': audio,
            'state': game_logic.get_state()
        }

        start_response('200 OK', [('Content-Type', 'application/json')])
        return [json.dumps(ndata).encode()]

    else:
        # If we are running alongside a web server then the server will handle static files.
        # This is for the stand-alone case (like running on the Farmer Says)
        fn = environ['PATH_INFO']
        if fn == '/':
            fn = '/index.html'
        print('*', fn, '*')
        with open('public' + fn, 'rb') as f:
            data = f.read()
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [data]


if __name__ == '__main__':
    try:
        from wsgiref.simple_server import make_server
        try:
            httpd = make_server('', 80, application)
            print('Serving on port 80...')
        except:
            httpd = make_server('', 8080, application)
            print('Serving on port 8080...')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Goodbye.')
