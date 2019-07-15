# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import pandas as pd

from ..d00_utils.db_utils import dbReadWriteRaw, dbReadWriteClean

def clean_measurement_abstract_rpt(df):
    """Clean measurement_abstract_rpt table.

    The following cleaning steps are performend:
        1. strip string columns: `name`, `unitname`
    
    :param df: measurement_abstract_rpt table as dataframe
    :return: cleaned dataframe
    
    """
    df.rename(columns={"studyid": "studyidk"}, inplace=True)
    
    for column in ["row_id", "studyidk", "measabstractnumber"]:
        df[column] = df[column].astype(int)
    
    for column in ["name", "unitname"]:
        df[column] = df[column].str.strip()
    print("Cleaned measurement_abstract_rpt table.")

    return df


def clean_measgraphref(df):
    """Clean measgraphref table.
    
    The following cleaning steps are performend:
        1. remove rows with empty `instanceidk` column
        2. transform `instanceidk` and `indexinmglist` values to integer datatype
        3. remove rows with negative values in `instanceidk` and `indexinmglist`
        4. drop `srinstanceidk` column           
    
    :param df: measgraphref table as dataframe
    :return: cleaned table as dataframe
    
    """
    df['instanceidk'] = df['instanceidk'].replace('', -1)
    
    for column in ["row_id", "studyidk", "measabstractnumber", "instanceidk", "indexinmglist"]:
        df[column] = pd.to_numeric(df[column], errors='coerce').astype(int)

    df_clean = df.drop("srinstanceidk", axis="columns")
    
    print("Cleaned measgraphref table.")

    return df_clean


def clean_measgraphic(df):
    """Clean measgraphic table.
    
    The following cleaning steps are performend:
        1. drop the following columns: ["graphictoolidk","longaxisindex",
                                        "measidk","loopidk","instancerecordtype"]
    
    :param df: measgraphic table as pandas dataframe
    :return: cleaned table as dataframe
    
    """
    for column in ["row_id", "instanceidk", "indexinmglist"]:
        df[column] = pd.to_numeric(df[column], errors='coerce').astype(int)
    
    df_clean = df.drop(columns=["graphictoolidk","longaxisindex","measidk",
                          "loopidk","instancerecordtype"])
    print("Cleaned measgraphic table.")

    return df_clean


def clean_study_summary(df):
    """Clean summary table.
    
    The following cleaning steps are performend:
        1. replace empty values with 1 in columns `age`, `patientweight`, `patientheight`
        2. replace `,` with `.` in columns `age`, `patientweight`, `patientheight`
    
    :param df: 
    :return: cleaned table as dataframe
    
    """
    # clean age, patientweight, patientheight columns
    for column in ['age', 'patientweight', 'patientheight']:
        df[column] = df[column].replace('', -1)
    
    for column in ["row_id", "studyidk", "age"]:
        df[column] = pd.to_numeric(df[column], errors='coerce').astype(int)
        
    for column in ["patientweight", "patientheight"]:
        df[column] = pd.to_numeric(df[column], errors='coerce')
    
    # remove outliers
    for column in ['age', 'patientweight', 'patientheight']:
        boxplot = plt.boxplot(df[column])
        outlier_min, outlier_max = [item.get_ydata()[0] for item in boxplot['caps']]
        df[column] = df[column].apply(lambda x: 1 if x > outlier_max else x)
        df[column] = df[column].apply(lambda x: 1 if x < outlier_min else x)

    # create BMI column and clean outliers
    # (formula from https://www.cdc.gov/nccdphp/dnpao/growthcharts/training/bmiage/page5_1.html)
    df['bmi'] = df.apply(lambda x: ((x.patientweight/x.patientheight/x.patientheight)*10000), axis=1)
    boxplot = plt.boxplot(df['bmi']);
    outlier_min, outlier_max = [item.get_ydata()[0] for item in boxplot['caps']]
    df['bmi'] = df['bmi'].apply(lambda x: 1 if x > outlier_max else x)
    df['bmi'] = df['bmi'].apply(lambda x: 1 if x < outlier_min else x)
    
    # clean gender column
    df['gender'] = df['gender'].replace('', 'U')
    
    # clean findingcode column
    df['findingcode'] = df['findingcode'].apply(lambda x: x.split(","))
    
    return df


def clean_tables():
    """Transforms raw tables and writes them to database schema 'clean'.
    """
    
    io_raw = dbReadWriteRaw()
    io_clean = dbReadWriteClean()
    
    tables_to_clean = {'measurement_abstract_rpt' : 'clean_measurement_abstract_rpt(tbl)', 
                       'a_measgraphref' : 'clean_measgraphref(tbl)', 
                       'a_measgraphic' : 'clean_measgraphic(tbl)', 
                       'dm_spain_view_study_summary' : 'clean_study_summary(tbl)'}

    for key, val in tables_to_clean.items():
        tbl = io_raw.get_table(key)
        clean_tbl = eval(val)
        
        io_clean.save_to_db(clean_tbl, key)
        print('Created table `'+key+'` in schema '+io_clean.schema)
        
if __name__ == '__main__':
    clean_tables()        