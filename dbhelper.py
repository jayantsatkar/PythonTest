import pymssql
from configparser import ConfigParser
from errorLogger import *


class DBHelper:
    def __init__(self):
        print('In DBHelper Contructor')
        
        

    @staticmethod
    def DBConnectionInfo():
        configur = ConfigParser()
        configur.read('config.ini')
        _server = str(configur.get('DataBase', 'server'))
        _user = str(configur.get('DataBase', 'user'))
        _password = str(configur.get('DataBase', 'password'))
        _database = str(configur.get('DataBase', 'database'))
        _asDict = bool(configur.get('DataBase', 'as_dict'))
        paramList = [_server, _user, _password, _database,_asDict]
        return paramList

    @staticmethod
    def ExecuteQuery(procname):
        logger = LogError.LogError()
        paramList = DBHelper.DBConnectionInfo()
        
        try:
            conn = pymssql.connect(server=paramList[0], user=paramList[1], password=paramList[2], database=paramList[3],as_dict=paramList[4])
            cursor = conn.cursor()
            cursor.execute(procname)
            records = cursor.fetchall()
            return records

        except Exception as e:
            print('Error occurred :: ', e)
            
            logger.info(msg='Application Started',exc_info = e)
            
        finally:
            conn.close()


    @staticmethod
    def ExecuteNonQuery(procname):
        paramList = DBHelper.DBConnectionInfo()
        logger.info(msg='Application Started',exc_info= e )
        conn = ''
        try:
            conn = pymssql.connect(server=paramList[0], user=paramList[1], password=paramList[2], database=paramList[3],as_dict=paramList[4])
            cursor = conn.cursor()
            cursor.execute(procname)
            # records = cursor.fetchall()
            # return records

        except Exception as e:
            print('Error occurred :: ', e)
            
        finally:
            conn.close()
            # conn.close()


