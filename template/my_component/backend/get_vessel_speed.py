

import pandas as pd
from sqlalchemy import create_engine 


def get_speed_of_vessels(imo_ls: list, engine):
    imo_ls = ','.join(imo_ls)
    # engine = create_engine("mssql+pyodbc://research:research@GEN-NT-SQL11\MATLAB:56094/BrokerData?driver=SQL+Server+Native+Client+10.0")    
    query = f"""
            SELECT   [ShipID]
            ,[MMSI]
            ,[ShipName]
            ,[Latitude]
            ,[Longitude]
            ,[Speed]
            ,[MovementdateTime]
            FROM [VTPositionDB].[dbo].[VTvesselposition_last]
            where [ShipID] in ({imo_ls})
        """
    df = pd.read_sql(query, engine) 
    return df