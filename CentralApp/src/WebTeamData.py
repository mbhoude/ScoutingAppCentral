'''
Created on Feb 7, 2013

@author: ksthilaire
'''

import os
import re
import web

import AttributeDefinitions
import DbSession
import DataModel

def get_datafiles(input_dir, pattern, recursive,logger):
    '''Get list of files to be displayed.

    Args:
        input_dir: Directory to search.
        pattern: Regular expression to use to filter files.
        recursive: Whether or not to recurse into input_dir.
        logger: logger for debug printing

    Returns:
        A list of files.
    '''
    
    # make sure that the directory path exists
    try: 
        os.makedirs(input_dir)
    except OSError:
        if not os.path.isdir(input_dir):
            raise

    file_list = []    
    
    if recursive:
        for root, dirs, files in os.walk(input_dir):
            logger.debug( 'Root: %s, Dirs: %s, Files: %s', root, dirs, files)
            for name in files:
                if pattern.match(name):
                    file_list.append(os.path.join(root, name))
    else:
        files = os.listdir(input_dir)
        logger.debug('Files: %s', files)
        for name in files:
            if pattern.match(name):
                file_list.append(os.path.join(input_dir, name))

    logger.debug('File List: %s', file_list)
    return file_list


def get_team_datafiles_page(global_config, name):
    
    global_config['logger'].debug( 'GET Team Data Files: %s', name )
    session = DbSession.open_db_session(global_config['db_name'])

    if global_config['attr_definitions'] == None:
        return None
    
    attrdef_filename = './config/' + global_config['attr_definitions']
    attr_definitions = AttributeDefinitions.AttrDefinitions()
    attr_definitions.parse(attrdef_filename)
    page=''
    
    team_info = DataModel.getTeamInfo(session, int(name))
    if team_info:
        page += '<h3>Team Info</h3>'
        page += '<li>Team Nickname: ' + team_info.nickname + '</li>'
        page += '<li>Motto: ' + team_info.motto + '</li>'
        page += '<li>Affiliation: ' + team_info.fullname + '</li>'
        page += '<li>Location: ' + team_info.location + '</li>'
        page += '<li>Rookie Season: ' + str(team_info.rookie_season) + '</li>'
        page += '<li>Website: <a href="' + team_info.website + '">' + team_info.website + '</a></li>'
        page += '<br>'
     
    competitions = []
    this_comp = global_config['this_competition']
    competitions.append(this_comp)
    competitions_str = global_config['other_competitions']
    competitions_str = competitions_str.replace(this_comp,'')
    if competitions_str.count(',') > 0:
        other_comps = competitions_str.split(',')
        for other_comp in other_comps:
            if other_comp != '':
                competitions.append(other_comp)
    elif competitions_str != '':
        competitions.append(competitions_str)
        
    for comp in competitions:
        if comp != '':
            input_dir = './static/data/' + comp + '/ScoutingData/'
            pattern = 'Team' + name + '_' + '[a-zA-Z0-9_]*.txt'
            datafiles = get_datafiles(input_dir, re.compile(pattern), False, global_config['logger'])
            
            input_dir = './static/data/' + comp + '/ScoutingPictures/'
            pattern = 'Team' + name + '_' + '[a-zA-Z0-9_]*.jpg|mp4'
            mediafiles = get_datafiles(input_dir, re.compile(pattern), False, global_config['logger'])
                        
            if len(datafiles) == 0 and len(mediafiles) == 0:
                continue
            
            page += '<hr>'
            page += '<h3> ' + comp + '</h3>'

            team_attributes = DataModel.getTeamAttributesInOrder(session, name, comp)
            if len(team_attributes) > 0:
                page += '<ul>'
                page += '<h3>Scouting Data Summary:</h3>'
                
                page += '<ul>'
                page += '<table border="1" cellspacing="5">'
                page += '<tr>'
                page += '<th>Attribute Name</th>'
                page += '<th>Matches</th>'
                page += '<th>Cumulative Value</th>'
                page += '<th>Average Value</th>'
                #page += '<th>Last Value</th>'
                page += '<th>All Values</th>'
                page += '</tr>'
    
                for attribute in team_attributes:
                    attr_def = attr_definitions.get_definition( attribute.attr_name )
                    include_attr = False
                    if attr_def:
                        if attr_def.has_key('Include_In_Team_Display') \
                                and attr_def['Include_In_Team_Display'] == 'Yes':
                                include_attr = True
                        elif attr_def.has_key('Include_In_Report') \
                                and attr_def['Include_In_Report'] == 'Yes':
                            include_attr = True
                        elif attr_def.has_key('Weight') \
                                and attr_def.has_key('Weight') != '0':
                            include_attr = True

                    if include_attr == True:   
                        page += '<tr>'
                        if attr_def.has_key('Display_Name'):
                            page += '<td>%s</td>' % attr_def['Display_Name']
                        else:
                            page += '<td>%s</td>' % attr_def['Name']
                            
                        page += '<td>%s</td>' % str(attribute.num_occurs)
                        page += '<td>%s</td>' % str(attribute.cumulative_value)
                        page += '<td>%0.2f</td>' % (attribute.avg_value)
                        #page += '<td>%s</td>' % str(attribute.attr_value)
                        page += '<td>%s</td>' % attribute.all_values
                        page += '</tr>'
                        
                page += '</table>'    
                page += '</ul>'
                page += '</ul>'

            if len(datafiles) > 0:         
                page += '<ul>'
                page += '<h3>Pit and Match Data:</h3>'
                page += '<ul>'
                for filename in datafiles:
                    segments = filename.split('/')
                    basefile = segments[-1]
                    # the following line inserts a hyperlink to the file itself, the second line
                    # inserts a hyperlink to a url that allows the webserver to create a nicer display of
                    # the file contents
                    #page += '<li><a href="' + filename.lstrip('.') + '">' + basefile + '</a></li>'
                    page += '<li><a href="' + '/ScoutingData/' + comp + '/' + basefile + '">' + basefile + '</a></li>'
                page += '</ul>'

            if len(mediafiles) > 0:         
                page += '<h3>Pictures and Videos:</h3>'
                page += '<ul>'
                for filename in mediafiles:
                    segments = filename.split('/')
                    basefile = segments[-1]
                    page += '<li><a href="' + filename.lstrip('.') + '">' + basefile + '</a></li>'
                page += '</ul>'
            page += '</ul>'
        
    page += '<hr>'
    page += '<h3> Notes for Team ' + name + '</h3>'
    page += '<ul>'
        
    comp = global_config['this_competition']        
    team_notes = DataModel.getTeamNotes(session, name, comp)
    for note in team_notes:
        page += '<li>' + note.data + '</li>'
    
    page += '</ul>'
    
    return page

def get_team_server_page(global_config, name):
        
    global_config['logger'].debug( 'GET Team Server: %s', name )
    
    session = DbSession.open_db_session(global_config['db_name'])
    
    web.header('Content-Type', 'application/json')
    result = []
    result.append('{ "attributes": [\n')
    comp = global_config['this_competition']
    team_attributes = DataModel.getTeamAttributes(session, name, comp)
    for attribute in team_attributes:
        result.append(attribute.json())
        result.append(',\n')
    if len(team_attributes) > 0:
        result = result[:-1]
    result.append(']}')
    return ''.join(result)

def get_team_score_page(global_config, name):
        
    global_config['logger'].debug( 'GET Team Score: %s', name )
    
    session = DbSession.open_db_session(global_config['db_name'])
    
    web.header('Content-Type', 'application/json')
    result = []
    result.append('{ "score": [')
    comp = global_config['this_competition']
    team_score = DataModel.getTeamScore(session, name, comp)
    for score in team_score:
        result.append(score.json())
        result.append(',\n')
    if len(team_score) > 0:
        result = result[:-1]
    result.append(']}')
    return ''.join(result)

def get_team_notes_page(global_config, name):
        
    global_config['logger'].debug( 'GET Team Notes: %s', name )
    
    session = DbSession.open_db_session(global_config['db_name'])
    
    #web.header('Content-Type', 'application/json')
    notes_string = ''
    comp = global_config['this_competition']
    team_notes = DataModel.getTeamNotes(session, name, comp)
    for note in team_notes:
        notes_string += note.data + '\n'
    return notes_string

def get_team_rankings_page(global_config, comp=None):
        
    global_config['logger'].debug( 'GET Team Rankings' )
    
    session = DbSession.open_db_session(global_config['db_name'])
        
    web.header('Content-Type', 'application/json')
    result = []
    result.append('{ "rankings": [\n')
    
    if comp == None:
        comp = global_config['this_competition']        
        
    team_rankings = DataModel.getTeamsInRankOrder(session, comp, False)
    for team in team_rankings:
        # round the score to an integer value
        team.score = float(int(team.score))
        result.append(team.json())
        result.append(',\n')
    if len(team_rankings) > 0:
        result = result[:-1]
    result.append(']}')
    return ''.join(result)

def get_team_rankings_array(global_config):
        
    global_config['logger'].debug( 'GET Team Rankings Array' )
    
    session = DbSession.open_db_session(global_config['db_name'])
        
    web.header('Content-Type', 'application/json')
    result = []
    result.append('[')
    comp = global_config['this_competition']        
    team_rankings = DataModel.getTeamsInRankOrder(session, comp)
    for team in team_rankings:
        data_str = '[%d,%d]' % (team.team,int(team.score))
        result.append(data_str)
        result.append(',')
    if len(team_rankings) > 0:
        result = result[:-1]
    result.append(']')
    return ''.join(result)


def get_team_attr_rankings_page(global_config, comp, attr_name):
        
    global_config['logger'].debug( 'GET Team Attribute Rankings' )
    
    session = DbSession.open_db_session(global_config['db_name'])
        
    attrdef_filename = './config/' + global_config['attr_definitions']
    attr_definitions = AttributeDefinitions.AttrDefinitions()
    attr_definitions.parse(attrdef_filename)
    attr = attr_definitions.get_definition(attr_name)
    try:
        stat_type = attr['Statistic_Type']
    except:
        stat_type = 'Total'

    web.header('Content-Type', 'application/json')
    result = []
    result.append('{ "rankings": [\n')
            
    team_rankings = DataModel.getTeamAttributesInRankOrder(session, comp, attr_name, False)
    for team in team_rankings:
        if stat_type == 'Average':
            value = int(team.cumulative_value/team.num_occurs)
        else:
            value = int(team.cumulative_value)
        data_str = '{ "team": %d, "value": %d }' % (team.team,value)
        result.append(data_str)
        result.append(',\n')
    if len(team_rankings) > 0:
        result = result[:-1]
        result.append('\n')
    result.append(']}')
    return ''.join(result)

def get_team_score_breakdown_page(global_config, name, comp=None):
        
    global_config['logger'].debug( 'GET Team Score Breakdown: %s', name )
    
    session = DbSession.open_db_session(global_config['db_name'])
    
    attrdef_filename = './config/' + global_config['attr_definitions']
    attr_definitions = AttributeDefinitions.AttrDefinitions()
    attr_definitions.parse(attrdef_filename)
    
    web.header('Content-Type', 'application/json')
    result = []

    result.append('{ "score_breakdown": [\n')
    if comp == None:
        comp = global_config['this_competition']        
    team_attributes = DataModel.getTeamAttributesInOrder(session, name, comp)
    for attribute in team_attributes:
        attr_def = attr_definitions.get_definition( attribute.attr_name )
        if attr_def:
            try:
                stat_type = attr_def['Statistic_Type']
            except:
                stat_type = 'Total'

            weight = int(float(attr_def['Weight']))
            if weight != 0:
                if stat_type == 'Average':
                    value = int(attribute.cumulative_value/attribute.num_occurs)
                else:
                    value = int(attribute.cumulative_value)
                data_str = '{"attr_name": "%s", "raw_score": %d, "weighted_score": %d}' % (attribute.attr_name,int(value),int(weight*value)) 
                result.append(data_str)
                result.append(',\n')
    if len(team_attributes) > 0:
        result = result[:-1]
        result.append('\n')
    result.append(']}')
    
    return ''.join(result)


def get_team_attributes_page(global_config):
        
    global_config['logger'].debug( 'GET Team Attributes' )
    
    session = DbSession.open_db_session(global_config['db_name'])
    
    attrdef_filename = './config/' + global_config['attr_definitions']
    attr_definitions = AttributeDefinitions.AttrDefinitions()
    attr_definitions.parse(attrdef_filename)
    
    web.header('Content-Type', 'application/json')
    result = []
    result.append('{ "attributes": [\n')
    comp = global_config['this_competition']        
    team_rankings = DataModel.getTeamsInRankOrder(session, comp)
    for team_entry in team_rankings:
        result.append("{ 'Team': " + str(team_entry.team))
        result.append(", 'Score': " + '%.2f' % team_entry.score )
        team_attributes = DataModel.getTeamAttributesInOrder(session, team_entry.team, comp)
        for attribute in team_attributes:
            attr_def = attr_definitions.get_definition( attribute.attr_name )
            if attr_def:
                weight = int(float(attr_def['Weight']))
                if weight != 0:
                    result.append( ", '" + attribute.attr_name + "': ")
                    if ( attr_def['Statistic_Type'] == 'Total'):
                        #result.append( str(attribute.cumulative_value) )
                        result.append( DataModel.mapValueToString(attribute.cumulative_value, attribute.all_values, attr_def, True) )
                    elif ( attr_def['Statistic_Type'] == 'Average'):
                        #result.append( str(attribute.avg_value) )
                        result.append( DataModel.mapValueToString(attribute.avg_value, attribute.all_values, attr_def, True) )
                    else:
                        #result.append( str(attribute.attr_value) )
                        result.append( DataModel.mapValueToString(attribute.attr_value, attribute.all_values, attr_def, True) )
                    
        result.append(' }')
        result.append(',\n')
    if len(team_rankings) > 0:
        result = result[:-1]
        result.append('\n')
    result.append(']}')
    return ''.join(result)

def get_team_datafile_page(global_config, filename):
        
    global_config['logger'].debug( 'GET Team Data File: %s', filename )
        
    comp, name = filename.split('/', 1)
    filepath = './static/data/' + comp + '/ScoutingData/' + name
    datafile = open( filepath, "r" )
    
    team = filename.split('_')[0].lstrip('Team')
    page =''
    page += '<table border="1" cellspacing="5">'    
    page += '<tr>'
    page += '<th>Attribute Name</th>'
    page += '<th>Attribute Value</th>'
    page += '</tr>'
    
    while 1:
        lines = datafile.readlines(100)
        if not lines:
            break
        for line in lines:
            line = line.rstrip('\n')
            name, value = line.split(':')
            
            page += '<tr>'
            page += '<td>' + name + '</td>'
            page += '<td>' + value + '</td>'
            page += '</tr>'
            
    page += '</table>'
    return page
