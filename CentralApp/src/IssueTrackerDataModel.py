#!/usr/bin/python
'''
Created on Jan 04, 2013

@author: ksthilaire
'''

import datetime
from sqlalchemy import create_engine
from sqlalchemy import schema
from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import sessionmaker
from optparse import OptionParser




class Base(object):
    '''
    Base class or all objects in the model.

    Provides basic property setting, and object to string conversion.
    Also provides methods for converting objects to json format.

    A little bit of python magic in the base, greatly reduces overall
    amount of code required to implement these features.

    This class extends the declarative_base() class supplied by
    SA ORM. The default constructor of declarative_base() automatically
    assigns instance members based on keyword arguments in the
    constructor. This means all model classes need to be
    instantiated with keywords arguments. (This helps with readability
    in any case.)
    '''

    # Common to all model classes.
    objectId = Column(Integer, primary_key=True)

    def __repr__(self):
        sb = []
        sb.append('<%s('%self.__class__.__name__)
        try:
            for c in self.__table__.columns:
                sb.append('"%s",'%getattr(self, c.name))
        except:
            # If this is a Base class instance, __table__
            # will not exist and we arrive here.
            pass

        sb.append(')>')

        return ''.join(sb)

    def todict(self):
        for x in self.__table__.columns:
            yield (x.name, getattr(self, x.name))

    def __iter__(self):
        return self.todict()

    def json(self):
        mystring = str(dict(self))
        mystring = mystring.replace(": u'", ": '")                
        return mystring


# Augment the sqlalchemy base.
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base(cls=Base)


class TeamRank(Base):
    __tablename__ = 'rankings'

    # Constructor parameters.
    team            = Column(Integer)
    competition     = Column(String(32))
    score           = Column(Float)

class TeamAttribute(Base):
    __tablename__ = 'attributes'

    # Constructor parameters.
    team             = Column(Integer)
    competition      = Column(String(32))
    attr_name        = Column(String(32), nullable=False)
    attr_value       = Column(Float)
    attr_type        = Column(String(32))
    num_occurs       = Column(Integer)
    cumulative_value = Column(Float)
    avg_value        = Column(Float)
    all_values       = Column(String(512))
    
class ProcessedFiles(Base):
    __tablename__ = "processed_files"

    filename = Column(String(256), nullable=False)

class NotesEntry(Base):
    __tablename__ = "team_notes"

    team        = Column(Integer)
    competition = Column(String(32))
    data        = Column(String(1024))
    tag         = Column(String(64))
    
def isFileProcessed(session, filename):
    

    file_list = session.query(ProcessedFiles).filter(ProcessedFiles.filename==filename).all()
    if len(file_list)>0:
        return True
    else:
        return False

def addProcessedFile(session, name):
    file_name = ProcessedFiles(filename=name)
    session.add(file_name)
    
def addNotesEntry(session, teamnum, comp, notes, notestag):
    notes = NotesEntry(team=teamnum, competition=comp, data=notes, tag=notestag)
    session.add(notes)
    
def getTeamNotes(session, teamId, comp):
    notes = session.query(NotesEntry).filter(NotesEntry.team==teamId).\
                                      filter(NotesEntry.competition==comp).all()
    print str(notes)
    return notes
        
def getTeamAttributes(session, teamId, comp):
    attrList = session.query(TeamAttribute).filter(TeamAttribute.team==teamId).\
                                      filter(TeamAttribute.competition==comp).all()
    print str(attrList)
    return attrList

def getTeamAttributesInOrder(session, teamId, comp):
    attrList = session.query(TeamAttribute).\
            filter(TeamAttribute.team==teamId).\
            filter(TeamAttribute.competition==comp).\
            order_by(TeamAttribute.attr_name).all()
    return attrList

def getTeamAttribute(session, team, comp, name):
    attrList = session.query(TeamAttribute).filter(TeamAttribute.team==team).\
                                            filter(TeamAttribute.competition==comp).\
                                            filter(TeamAttribute.attr_name==name)
    return attrList.first()

def getTeamsInRankOrder(session, comp, max_teams=100):
    teamList = session.query(TeamRank).\
            filter(TeamRank.competition==comp).\
            order_by(TeamRank.score.desc()).\
            all()    
    return teamList

def getTeamsInNumericOrder(session, max_teams=100):
    teamList = session.query(TeamRank).\
            order_by(TeamRank.team).\
            all()    
    return teamList

def getTeamScore(session, teamId, comp):
    return session.query(TeamRank).filter(TeamRank.team==teamId).\
                                   filter(TeamRank.competition==comp).all()
        
def calculateTeamScore(session, teamId, comp, attr_defs):
    attributes = session.query(TeamAttribute).filter(TeamAttribute.team==teamId).\
                                              filter(TeamAttribute.competition==comp).all()
    total = 0.0
    for item in attributes:
        item_def = attr_defs.get_definition(item.attr_name)
        weight = item_def['Weight']
        # only include attributes with statistics types other than 'None'
        if item_def['Statistic_Type'] == 'Average':
            total += float(weight)*item.avg_value
        elif item_def['Statistic_Type'] == 'Total':
            total += float(weight)*item.cumulative_value

    return total
    
def setTeamScore(session, teamId, comp, score):
    teamList = session.query(TeamRank).filter(TeamRank.team==teamId).\
                                       filter(TeamRank.competition==comp).all()    
    if len(teamList)>0:
        team = teamList[0]
        team.team=teamId
        team.score=score
        print team.json()
    else:
        team = TeamRank(team=teamId, competition=comp, score=score)
        session.add(team)

def mapValueFromString(string_value, map_values):
    
    values = string_value.split(',')
    for value in values:
        tokens = map_values.split(':')
        for token in tokens:
            name, token_val = token.split('=')
            if name == value:
                mapped_value = token_val
                break
    return mapped_value

def mapValueToString(value, all_values, attr_def, need_quote=False):
    if attr_def['Type'] == 'Map_Integer':
        value_list = all_values.split(':')
        unique_values = []
        for item in value_list:
            single_value_list = item.split(',')
            for single_item in single_value_list:
                if len(unique_values) == 0:
                    unique_values.append( single_item )
                else:
                    found_match = False
                    for value in unique_values:
                        if ( value == single_item ):
                            found_match = True
                    if found_match == False:
                        unique_values.append( single_item )
        value_string = ''
        if ( need_quote == True ):
            value_string = "'"
        for index in range(len(unique_values)):
            if index == 0:
                value_string += unique_values[index]
            else:
                value_string += '-' + unique_values[index]
        if ( need_quote == True ):
            value_string += "'"
        return value_string
    else:
        return str(value)
    
        
def createOrUpdateAttribute(session, team, comp, name, value, attribute_def):
    attrList = session.query(TeamAttribute).filter(TeamAttribute.team==team).\
                                            filter(TeamAttribute.competition==comp).\
                                            filter(TeamAttribute.attr_name==name)
    attr = attrList.first()
    attr_type = attribute_def['Type']
    date = datetime.datetime.now(); #gets the current date and time down to the microsecond
    
    if attr_type == 'String':
        addNotesEntry(session, team, comp, value, date)
    else:
        attr_value = convertValues(attr_type, value, attribute_def)
    
        if attr:
            attr.attr_value = attr_value
            attr.num_occurs+=1
            attr.cumulative_value += attr_value
            attr.avg_value = attr.cumulative_value / attr.num_occurs
            attr.all_values += ':' + value
            print attr.json()
        else:
            attr = TeamAttribute(team=team, competition=comp, attr_name=name, 
                                 attr_type=attr_type, num_occurs=1,
                                 attr_value=attr_value, cumulative_value=attr_value, 
                                 avg_value=attr_value, all_values=value)
            session.add(attr)
            print attr.json()
        
def convertValues(attr_type, value, attribute_def):
    if attr_type == 'Float':
        attr_value = float(value)
    elif attr_type == 'Integer':
        attr_value = float(value)
    elif attr_type == 'Map_Integer':
        attr_value = float(mapValueFromString(value, attribute_def['Map_Values']))
    return attr_value

def deleteAllProcessedFiles(session):
    p_list = session.query(ProcessedFiles).all()
    for item in p_list:
        session.delete(item)
    session.flush()
    
def deleteAllTeamAttributes(session):
    a_list = session.query(TeamAttribute).all()
    for item in a_list:
        session.delete(item)
    session.flush()

def deleteAllTeamNotes(session):
    n_list = session.query(NotesEntry).all()
    for item in n_list:
        session.delete(item)
    session.flush()
    
def deleteAllTeamRanks(session):
    r_list = session.query(TeamRank).all()
    for item in r_list:
        session.delete(item)
    session.flush()
    
def create_db_tables(my_db):
    Base.metadata.create_all(my_db)

def dump_db_tables(my_db):
    meta = schema.MetaData(my_db)
    meta.reflect()
    meta.drop_all()

# The run_test method contains just a bunch of little operations to test out how the various
# database mechanisms work...    
def run_test():
    Session = sessionmaker(bind=my_db)
    session = Session()
    
    myteam=1075
    mycomp='TestComp'
    myattr='Teleop_Points'
    myvalue='42'

    # Build the attribute definition dictionary from the definitions csv file
    attrdef_filename = 'AttributeDefinitions-reboundrumble.xlsx'    
    attr_definitions = AttributeDefinitions.AttrDefinitions()
    attr_definitions.parse(attrdef_filename)
    attr_definition = attr_definitions.get_definition(myattr)
    attr_type = attr_definition['Type']
    attr_value = convertValues(attr_type, myvalue, attr_definition)

    # create a query that will search the database for all records that match the specified
    # team
    q1 = session.query(TeamRank).filter(TeamRank.team==myteam).filter(TeamRank.competition==mycomp)
    if q1:
        a = q1.first()
        # retrieve the first element that matches the team number. If there is one,
        # then we'll just print it out. If not, then we'll create an instance and 
        # add it to the database
        if a: 
            print str(a)
            print a.json()
        else:
            a1 = TeamRank(team=myteam, competition=mycomp, score=42.0)
            print str(a1)
            print a1.json()
            session.add(a1)

    # create a query that retrieves the first record that matches the team and attribute
    # if the attribure is found, then modify it in some way and store the new values
    # if the attribute is not found, then create an instance and add it to the
    # database
    q2 = session.query(TeamAttribute).filter(TeamAttribute.team==myteam and TeamAttribute.competition==mycomp and TeamAttribute.attr_name==myattr)
    if q2:
        b = q2.first()
        if b:
            b.attr_value+=5
            b.num_occurs+=1
            print str(b)
            print b.json()
        else:
            b1 = TeamAttribute(team=myteam, competition=mycomp, attr_name=myattr, attr_value=attr_value, 
                               cumulative_value=attr_value, attr_type=attr_type, num_occurs=1, avg_value=attr_value,
                               all_values=myvalue)
            print str(b1)
            print b1.json()
            session.add(b1)

    # retrieve a list of all the attributes from the database for the specified team using a 
    # utility method and print them out          
    myteam=1073
    allAttr = getTeamAttributes( session, myteam, mycomp )
    for d in allAttr:
        print d.json()        

    # given that same list, find a specific attribute in the list and update it
    # this loop construct is a nested for loop in one line...
    attr = next((i for i in allAttr if i.attr_name == myattr), None)
    if attr is not None:
        # attribute is found, so update the attribute with the new values
        attr.attr_value+=5
        attr.num_occurs+=1
        print attr.json()
    else:
        # attribute is not found, so create a new instance and add it to the database
        attr = TeamAttribute(team=myteam, competition=mycomp, attr_name=myattr, attr_value=attr_value, 
                             cumulative_value=attr_value, attr_type=attr_type, num_occurs=1, avg_value=attr_value,
                             all_values=myvalue)
        session.add(attr)
        print attr.json()
        
    # retrieve an ordered list of all teams in descending order (#1 team is first)
    rankList = getTeamsInRankOrder(session, mycomp)      
    for t in rankList:
        print t.json()        
    
    # exercise the attribute create/update utility method
    if (attr_definition['Database_Store']=='Yes'):
        createOrUpdateAttribute(session, myteam, mycomp, myattr, myvalue, attr_definition)
                    
    session.commit()


if __name__ == '__main__':

    parser = OptionParser()

    # db options.
    parser.add_option(
        "-u","--user",dest="user", default='root', help='Database user name')
    parser.add_option(
        "-d","--db",dest="db", default='test', help='Database name')
    parser.add_option(
        "-p","--password",dest="password", default='team1073',
        help='Database password')

    # action options.
    parser.add_option(
        "-t","--test",action="store_true", dest="test", default=False,
        help='Run simple tests')
    parser.add_option(
        "-b","--dbtype",dest="dbtype", default='sqlite',
        help='Select database type (mysql or sqlite')
    parser.add_option(
        "-c","--create",action="store_true", dest="create", default=False,
        help='Create database schema')
    parser.add_option(
        "-D","--drop",action="store_true", dest="drop", default=False,
        help='Drop database schema')
   
    # parse command line.
    (options,args) = parser.parse_args()

    # run!
    if options.dbtype == 'sqlite':
        db_connect='sqlite:///%s'%(options.db)
    elif options.dbtype == 'mysql':
        db_connect='mysql://%s:%s@localhost/%s'%(options.user, options.password, options.db)
    else:
        raise Exception("No Database Type Defined!")

    my_db = create_engine(db_connect)

    if options.create:
        Base.metadata.create_all(my_db)

    # Dump the contents of the database if requested through the command option
    if options.drop:
        dump_db_tables(my_db)

    if options.test:
        run_test()


