
def get_html_head(title_str = 'FIRST Team 1073 - The Force Team'):
    head_str  = '<head>\n'
    head_str += '<meta charset="utf-8" />\n'
    head_str += '<title>%s</title>\n' % title_str
    head_str += '<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=1, minimum-scale=0.0, maximum-scale=2.0" />\n'
    head_str += '<link rel="shortcut icon" href="/static/media/images/1073-favicon.ico" type="image/x-icon" />\n'
    head_str += '<link rel="stylesheet" href="/static/media/css/style.css" type="text/css" media="screen" />\n'

    head_str += '	<style type="text/css" title="currentStyle">\n'
    head_str += '		@import "/static/media/css/demo_page.css";\n'
    head_str += '		@import "/static/media/css/demo_table.css";\n'
    head_str += '	</style>\n'

    head_str += '<script type="text/javascript" language="javascript" src="/static/media/js/jquery.js"></script>\n'
    head_str += '<script type="text/javascript" language="javascript" src="/static/media/js/jquery.dataTables.js"></script>\n'
    head_str += '</head>\n'
    
    return head_str