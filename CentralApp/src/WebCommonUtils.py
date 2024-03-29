import os
import AttributeDefinitions
import DbSession
import DataModel
import WebEventData

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

import ScoutingAppMainWebServer

def get_comp_list():
    
    my_config = ScoutingAppMainWebServer.global_config
    complist = list()
    season = my_config['this_season']
    this_comp = my_config['this_competition']
    complist.append(this_comp+season)
    
    other_competitions = my_config['other_competitions'].split(',')

    for comp in other_competitions:
        if comp and comp != my_config['this_competition']:
            complist.append(comp+season)

    return complist

def get_short_comp_list(season=None):
    
    my_config = ScoutingAppMainWebServer.global_config
    complist = list()
    if season == None:
        season = my_config['this_season']
    this_comp = my_config['this_competition']
    complist.append(this_comp)
    
    other_competitions = my_config['other_competitions'].split(',')

    for comp in other_competitions:
        if comp and comp != my_config['this_competition']:
            complist.append(comp)

    return complist

# retrieve the list of competitions that the specified team has been scouted, including this competition
def get_team_comp_list(this_comp, team):
    
    my_config = ScoutingAppMainWebServer.global_config
    complist = list()
    
    if this_comp == None:
        this_comp = my_config['this_competition'] + my_config['this_season']
        
    complist.append(this_comp)
    
    session = DbSession.open_db_session(my_config['db_name'])
    team_scores = DataModel.getTeamScore(session, team)
    for score in team_scores:
        comp = score.competition
        # currently, the competition season is stored in the database
        # as part of the competition. So, we need to add it for the comparison,
        # but not as we define the complist itself
        if comp != this_comp:
            complist.append(comp)
    return complist

# retrieve a list of team info name/value pairs
def get_team_info_str(team):
    
    my_config = ScoutingAppMainWebServer.global_config
    session = DbSession.open_db_session(my_config['db_name'])

    team_info_str=list()
    team_info = DataModel.getTeamInfo(session, int(team))
    if team_info:
        team_info_str.append(('Team Nickname',team_info.nickname,'string'))
        team_info_str.append(('Affiliation',team_info.fullname,'string'))
        team_info_str.append(('Location',team_info.location,'string'))
        team_info_str.append(('Rookie Season',team_info.rookie_season,'string'))
        team_info_str.append(('Website',team_info.website,'link'))
    return team_info_str

def get_issue_types():
    my_config = ScoutingAppMainWebServer.global_config
    issue_types = my_config['issue_types'].split(',')
    return issue_types

def get_attr_list():
    my_config = ScoutingAppMainWebServer.global_config
    attr_list = list()
    
    attrdef_filename = './config/' + my_config['attr_definitions']
    if os.path.exists(attrdef_filename):
        attr_definitions = AttributeDefinitions.AttrDefinitions()
        attr_definitions.parse(attrdef_filename)
        attr_dict = attr_definitions.get_definitions()
        attr_list = attr_dict.keys()
        attr_list.sort()
                
    return attr_list

def get_file_list(dir_name,thumbnail_size=None):
    file_list = []    

    # if the directory name starts with a slash, prepend a '.' to make it a relative
    # path from this point.
    if dir_name.startswith('/'):
        dir_name = '.' + dir_name
                
    for root, dirs, files in os.walk(dir_name):
        # strip off any leading '.' in the root path so that the resulting entry
        # will have an absolute path
        root = root.lstrip('.')
        
        #print 'Root:', root, ' Dirs: ', dirs, ' Files:', files
        for name in files:
            # build the path to the file by joining the root with the filename.
            # note that we will replace any backslash in the resulting path with forward
            # slashes
            file_path = os.path.join(root,name).replace('\\','/')
            if thumbnail_size != None:
                thumbnail_name = thumbnail_size + '_' + name
                thumbnail_path = os.path.join(root+'/Thumbnails/', thumbnail_name).replace('\\','/')
                file_entry = (file_path, name,thumbnail_path)
            else:
                # create a tuple with the path and the file name so that a hyperlink can be easily 
                # generated from the file entry
                file_entry = (file_path, name)
            
            # and append the entry to the list
            file_list.append(file_entry)
                
    return file_list

def get_event_info_str(event_name, season=None):
    my_config = ScoutingAppMainWebServer.global_config
    
    if event_name.startswith('201'):
        year = event_name[0:4]
        event_code = event_name[4:]
    else:
        if season == None:
            year = my_config['this_season']
        else:
            year = season
        event_code = event_name

    event_dict = WebEventData.get_event_info_dict(my_config, year, event_code)

    event_info_str=list()
    if event_dict:
        event_info_str.append(('Name',event_dict['name'],'string'))
        event_info_str.append(('Code',event_dict['event_code'].upper(),'string'))
        event_info_str.append(('Location',event_dict['location'],'string'))
        event_info_str.append(('Start Date',event_dict['start_date'],'string'))
        event_info_str.append(('End Date',event_dict['end_date'],'string'))
    else:
        event_info_str = None

    return event_info_str

def map_event_code_to_comp(event_name, season=None):
    my_config = ScoutingAppMainWebServer.global_config
    
    if season == None:
        if event_name.startswith('201'):
            season = event_name[0:4]
        else:
            season = my_config['this_season']
    
    #TODO: Need to replace this hardcoded behavior with something more dynamic/configurable
    #       We may also just want to adopt the FIRST short event codes, too, though they
    #       aren't all that obvious what they refer to.
    comp = event_name[4:] + season
    if comp == 'mabos':
        comp = 'NU' + season
    elif comp == 'nhdur':
        comp = 'UNH' + season
    elif comp == 'rismi':
        comp = 'RI' + season
    elif comp == 'necmp':
        comp = 'NECMP' + season
    else:
        pass
            
    return comp        

def map_event_code_to_short_comp(event_name, season=None):
    my_config = ScoutingAppMainWebServer.global_config
    
    if season == None:
        if event_name.startswith('201'):
            season = event_name[0:4]
        else:
            season = my_config['this_season']
    
    #TODO: Need to replace this hardcoded behavior with something more dynamic/configurable
    #       We may also just want to adopt the FIRST short event codes, too, though they
    #       aren't all that obvious what they refer to.
    comp = event_name[4:]
    if comp == 'mabos':
        comp = 'NU'
    elif comp == 'nhdur':
        comp = 'UNH'
    elif comp == 'rismi':
        comp = 'RI'
    elif comp == 'necmp':
        comp = 'NECMP'
    else:
        pass
            
    return comp        

def map_event_code_to_season(event_name):
    my_config = ScoutingAppMainWebServer.global_config
    if event_name.startswith('201'):
        season = event_name[0:4]
    else:
        season = my_config['this_season']
                
    return season        

def map_comp_to_event_code(comp):
    my_config = ScoutingAppMainWebServer.global_config
    
    #TODO: Need to replace this hardcoded behavior with something more dynamic/configurable
    #       We may also just want to adopt the FIRST short event codes, too, though they
    #       aren't all that obvious what they refer to.
    if len(comp) > 4:
        season_str = comp[-4:]
        if season_str[0] == '2' and season_str[1] == '0' and season_str[2] == '1':
            comp = comp[0:-4]
            
    comp = comp.lower()
    if comp == 'nu':
        event_code = 'mabos'
    elif comp == 'unh':
        event_code = 'nhdur'
    elif comp == 'ri':
        event_code = 'rismi'
    elif comp == 'necmp':
        event_code = 'necmp'
    else:
        event_code = comp
            
    return event_code        
    
def map_comp_to_season(comp):
    my_config = ScoutingAppMainWebServer.global_config
    
    season = my_config['this_season']
    
    # now overwrite the season if the competition string has an embedded year
    if len(comp) > 4:
        season_str = comp[-4:]
        if season_str[0] == '2' and season_str[1] == '0' and season_str[2] == '1':
            season = season_str
    
    return season

def get_district_string():
    
    my_config = ScoutingAppMainWebServer.global_config
    
    try:
        district_string = my_config['my_district']
    except:
        district_string = 'District'
        
    return district_string
