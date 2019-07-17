# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 09:26:54 2019

@author: court
"""
from src.d00_utils.db_utils import dbReadWriteClean, dbReadWriteViews
import pandas as pd
import numpy as np

def create_seg_view():
    """
    Produces a table of labelled volume mask segmentations
    The following steps are performend:
        1. Import a_modvolume, a_measgraphref, a_measgraphic, 
            measurement_abstract_rpt
        2. Create df by merging a_modvolume, a_measgraphref, a_measgraphic 
            based on 'instanceidk' and 'indexinmglist'
        3. Add measurement_abstract_rpt to df by merging on 'studyidk' 
            and 'measabstractnumber'
        4. Drop instance id 1789286 and  3121715 due to problems linking and 
            conflicts
        5. Create one hot encoded columns for measurements of interest based
            on measurement names
        6. Create one shot encode columns for segment names based on one 
            hot encoded columns for measurements
        7. Drop one hot encoded columns for measurements of interest
    
    :param: 
    :return df: the merge dataframe containing the segment labels
    """

    io_clean = dbReadWriteClean()
    io_views = dbReadWriteViews()
    
    # 1. Import a_modvolume, a_measgraphref, a_measgraphic, 
    #        measurement_abstract_rpt
    a_modvolume_df = io_clean.get_table('a_modvolume')
    a_measgraphref_df = io_clean.get_table('a_measgraphref')
    a_measgraphic_df = io_clean.get_table('a_measgraphic')
    measurement_abstract_rpt_df = io_clean.get_table('measurement_abstract_rpt')
    
    # 2. merge a_measgraphref_df, measurement_abstract_rpt_df
    df = pd.merge(a_measgraphref_df,measurement_abstract_rpt_df, how='left'
              , on=['studyidk','measabstractnumber'])
    del a_measgraphref_df
    del measurement_abstract_rpt_df
  
    #3. Create one hot encoded columns for measurements of interest based
    #        on measurement names
    df['AVItd ap4'] = pd.np.where(df.name.str.contains("AVItd ap4"), True, False)
    df['DVItd ap4'] = pd.np.where(df.name.str.contains('DVItd ap4'), True, False)
    df['VTD(el-ps4)'] = pd.np.where(df.name.str.contains('VTD\(el-ps4\)'), True, False)
    df['VTD(MDD-ps4)'] = pd.np.where(df.name.str.contains('VTD\(MDD-ps4\)'), True, False)
    
    df['AVIts ap4'] = pd.np.where(df.name.str.contains('AVIts ap4'), True, False)
    df['DVIts ap4'] = pd.np.where(df.name.str.contains("DVIts ap4"), True, False)
    df['VTS(el-ps4)'] = pd.np.where(df.name.str.contains("VTS\(el-ps4\)"), True, False)
    df['VTS(MDD-ps4)'] = pd.np.where(df.name.str.contains("VTS\(MDD-ps4\)"), True, False)
    
    df['AVItd ap2'] = pd.np.where(df.name.str.contains("AVItd ap2"), True, False)
    df['DVItd ap2'] = pd.np.where(df.name.str.contains('DVItd ap2'), True, False)
    df['VTD(el-ps2)'] = pd.np.where(df.name.str.contains('VTD\(el-ps2\)'), True, False)
    df['VTD(MDD-ps2)'] = pd.np.where(df.name.str.contains('VTD\(MDD-ps2\)'), True, False)
    
    df['AVIts ap2'] = pd.np.where(df.name.str.contains("AVIts ap2"), True, False)
    df['DVIts ap2'] = pd.np.where(df.name.str.contains('DVIts ap2'), True, False)
    df['VTS(el-ps2)'] = pd.np.where(df.name.str.contains('VTS\(el-ps2\)'), True, False)
    df['VTS(MDD-ps2)'] = pd.np.where(df.name.str.contains('VTS\(MDD-ps2\)'), True, False)
    
    df['Vol. AI (MOD-sp4)'] = pd.np.where(df.name.str.contains("Vol. AI \(MOD-sp4\)"), True, False)
    df['Vol. AI (MOD-sp2)'] = pd.np.where(df.name.str.contains('Vol. AI \(MOD-sp2\)'), True, False)
        
    #4. Create one shot encode columns for segment names based on one 
    #        hot encoded columns for measurements
    df['A4C_Ven_ED'] = (np.where(((df['AVItd ap4'] == True)| 
            (df['DVItd ap4'] == True)|
            (df['VTD(el-ps4)'] == True)|
            (df['VTD(MDD-ps4)'] == True)) , True, False))

    df['A4C_Ven_ES'] = (np.where(((df['AVIts ap4'] == True)| 
            (df['DVIts ap4'] == True)|
            (df['VTS(el-ps4)'] == True)|
            (df['VTS(MDD-ps4)'] == True)), True, False))
    
    df['A2C_Ven_ED'] = np.where(((df['AVItd ap2'] == True)|
            (df['DVItd ap2'] == True)|
            (df['VTD(el-ps2)'] == True)|
            (df['VTD(MDD-ps2)'] == True)), True, False)
    
    df['A2C_Ven_ES'] = np.where(((df['AVIts ap2'] == True)| 
            (df['DVIts ap2'] == True)|
            (df['VTS(el-ps2)'] == True)|
            (df['VTS(MDD-ps2)'] == True)), True, False)
    
    df['A4C_Atr_ES'] = np.where((df['Vol. AI (MOD-sp4)'] == True), True, False)
    df['A2C_Atr_ES'] = np.where((df['Vol. AI (MOD-sp2)'] == True), True, False)

    # 5. Drop one hot encoded columns for measurements of interest
    df.drop(['AVItd ap4', 'DVItd ap4', 'VTD(el-ps4)', 'VTD(MDD-ps4)'
             , 'AVIts ap4', 'DVIts ap4', 'VTS(el-ps4)', 'VTS(MDD-ps4)'
             , 'AVItd ap2', 'DVItd ap2', 'VTD(el-ps2)', 'VTD(MDD-ps2)'
             , 'AVIts ap2', 'DVIts ap2', 'VTS(el-ps2)', 'VTS(MDD-ps2)'
             , 'Vol. AI (MOD-sp4)', 'Vol. AI (MOD-sp2)'], axis=1 , inplace=True)
    
    # 6. Cut the dataframe to relevant columns as drop duplicates
    df_1 = df[['studyidk', 'instanceidk', 'indexinmglist', 'A4C_Ven_ED', 'A4C_Ven_ES', 'A2C_Ven_ED', 'A2C_Ven_ES'
           , 'A4C_Atr_ES', 'A2C_Atr_ES']].copy()
    del df
    df_2 = df_1.drop_duplicates()
    del df_1
    
    #  7. merge with a_measgraphic_df for frame number
    df_3 = pd.merge(df_2, a_measgraphic_df, how='left'
              , on=['instanceidk','indexinmglist'])
    del df_2
    del a_measgraphic_df

    # 8. Cut the dataframe to relevant columns as drop duplicates
    df_4 = df_3[['studyidk', 'instanceidk', 'indexinmglist', 'A4C_Ven_ED'
                 , 'A4C_Ven_ES', 'A2C_Ven_ED', 'A2C_Ven_ES', 'A4C_Atr_ES'
                 , 'A2C_Atr_ES', 'frame']].copy()
    del df_3

    
    # 8. merge with a_modvolume
    df_5 = pd.merge(a_modvolume_df, df_4, how='left'
                  , on=['instanceidk','indexinmglist'])
    del df_4
    del a_modvolume_df

    #4. Drop instance id 1789286 and 3121715 due to problems linking and 
    #        conflicts
    #   Drop unnessecary row_id from orginal tables (causes problems in dbWrite)
    df_6 = df_5.drop(df_5[(df_5.instanceidk == 1789286)|(df_5.instanceidk == 3121715)].index)
    del df_5
    
    # write output to db
    io_views.save_to_db(df_6, 'frames_by_volume_mask') 