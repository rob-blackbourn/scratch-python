"""Load the USDA Nutritional database"""

from __future__ import print_function

import os.path
import sqlalchemy as sa
import pandas as pd
import numpy as np

FD_GROUP_TABLE_NAME="fd_group"
FD_GROUP_KEYS=['FdGrp_Cd']

def _defineFoodGroupTable(metadata):
    return sa.Table(
        FD_GROUP_TABLE_NAME,
        metadata,
        sa.Column('FdGrp_Cd', sa.String(4), nullable=False, comment='4-digit code identifying a food group. Only the first 2 digits are currently assigned. In the future, the last 2 digits may be used. Codes may not be consecutive.'),
        sa.Column('FdGrp_Desc', sa.String(60), nullable=False, comment='Name of food group.'),
        sa.PrimaryKeyConstraint(*FD_GROUP_KEYS)
    )

def _saveFoodGroupsToSql(engine, df):
    df.set_index(FD_GROUP_KEYS).to_sql(FD_GROUP_TABLE_NAME, con=engine, if_exists='append')

FOOD_DES_TABLE_NAME="food_des"
FOOD_DES_KEYS=['NDB_No']

def _defineFoodDescriptionTable(metadata):
    return sa.Table(
        FOOD_DES_TABLE_NAME,
        metadata,
        sa.Column('NDB_No', sa.String(5), nullable=False, comment='5-digit Nutrient Databank number that uniquely identifies a food item. If this field is defined as numeric, the leading zero will be lost.'),
        sa.Column('FdGrp_Cd', sa.String(4), nullable=False, comment='4-digit code indicating food group to which a food item belongs.'),
        sa.Column('Long_Desc', sa.String(200), nullable=False, comment='200-character description of food item.'),
        sa.Column('Shrt_Desc', sa.String(60), nullable=False, comment='60-character abbreviated description of food item. Generated from the 200-character description using abbreviations in Appendix A. If short description is longer than 60 characters, additional abbreviations are made.'),
        sa.Column('ComName', sa.String(100), nullable=True, comment='Other names commonly used to describe a food, including local or regional names for various foods, for example, "soda" or "pop" for "carbonated beverages."'),
        sa.Column('ManufacName', sa.String(65), nullable=True, comment='Indicates the company that manufactured the product, when appropriate.'),
        sa.Column('Survey', sa.Boolean, nullable=True, comment='Indicates if the food item is used in the USDA Food and Nutrient Database for Dietary Studies (FNDDS) and thus has a complete nutrient profile for the 65 FNDDS nutrients.'),
        sa.Column('Ref_desc', sa.String(135), nullable=True, comment='Description of inedible parts of a food item (refuse), such as seeds or bone.'),
        sa.Column('Refuse', sa.Numeric(2, 0), nullable=True, comment='Percentage of refuse.'),
        sa.Column('SciName', sa.String(65), nullable=True, comment='Scientific name of the food item. Given for the least processed form of the food (usually raw), if applicable.'),
        sa.Column('N_Factor', sa.Numeric(4, 2), nullable=True, comment='Factor for converting nitrogen to protein (see p. 12).'),
        sa.Column('Pro_Factor', sa.Numeric(4, 2), nullable=True, comment='Factor for calculating calories from protein (see p. 13).'),
        sa.Column('Fat_Factor', sa.Numeric(4, 2), nullable=True, comment='Factor for calculating calories from fat (see p. 13).'),
        sa.Column('CHO_Factor', sa.Numeric(4, 2), nullable=True, comment='Factor for calculating calories from carbohydrate (see p. 13).'),
        sa.PrimaryKeyConstraint(*FOOD_DES_KEYS),
        sa.ForeignKeyConstraint(['FdGrp_Cd'], [FD_GROUP_TABLE_NAME + '.FdGrp_Cd'])
    )

def _saveFoodDescriptionsToSql(engine, df):
    df.set_index(FOOD_DES_KEYS).to_sql(FOOD_DES_TABLE_NAME, con=engine, if_exists='append')

WEIGHTS_TABLE_NAME="weights"
WEIGHTS_KEYS = ['NDB_No', 'Seq']

def _defineWeightsTable(metadata):
    return sa.Table(
        WEIGHTS_TABLE_NAME,
        metadata,
        sa.Column('NDB_No', sa.String(5), nullable=False, comment='5-digit Nutrient Databank number.'),
        sa.Column('Seq', sa.String(2), nullable=False, comment='Sequence number.'),
        sa.Column('Amount', sa.Numeric(7, 4), nullable=False, comment='Unit modifier (for example, 1 in "1 cup").'),
        sa.Column('Msre_Desc', sa.String(84), nullable=False, comment='Description (for example, cup, diced, and 1-inch pieces).'),
        sa.Column('Gm_Wgt', sa.Numeric(8, 2), nullable=False, comment='Gram weight.'),
        sa.Column('Num_Data_Pts', sa.Numeric(4, 0), nullable=True, comment='Number of data points.'),
        sa.Column('Std_Dev', sa.Numeric(7, 3), nullable=True, comment='Standard deviation.'),
        sa.PrimaryKeyConstraint(*WEIGHTS_KEYS),
        sa.ForeignKeyConstraint(['NDB_No'], [FOOD_DES_TABLE_NAME + '.NDB_No'])
    )

def _saveWeightsToSql(engine, df):
    df.set_index(WEIGHTS_KEYS).to_sql(WEIGHTS_TABLE_NAME, con=engine, if_exists='append')

NUTR_DEF_TABLE_NAME="nutr_def"
NUTR_DEF_KEYS=['Nutr_No']

def _defineNutrientDefinitionTable(metadata):
    return sa.Table(
        NUTR_DEF_TABLE_NAME,
        metadata,
        sa.Column('Nutr_No', sa.String(3), nullable=False, comment='Unique 3-digit identifier code for a nutrient.'),
        sa.Column('Units', sa.String(7), nullable=False, comment='Units of measure (mg, g, and so on).'),
        sa.Column('Tagname', sa.String(20), nullable=True, comment='International Network of Food Data Systems (INFOODS) Tagnames. A unique abbreviation for a nutrient/food component developed by INFOODS to aid in the interchange of data.'),
        sa.Column('NutrDesc', sa.String(60), nullable=False, comment='Name of nutrient/food component.'),
        sa.Column('Num_Dec', sa.Numeric(1, 0), nullable=False, comment='Number of decimal places to which a nutrient value is rounded.'),
        sa.Column('SR_Order', sa.Numeric(6, 0), nullable=False, comment='Used to sort nutrient records in the same order as various reports produced from SR.'),
        sa.PrimaryKeyConstraint(*NUTR_DEF_KEYS)
    )

def _saveNutrientDefinitionsToSql(engine, df):
    df.set_index(NUTR_DEF_KEYS).to_sql(NUTR_DEF_TABLE_NAME, con=engine, if_exists='append')

SRC_CD_TABLE_NAME="src_cd"
SRC_CD_KEYS=["Src_Cd"]

def _defineSourceCodeTable(metadata):
    return sa.Table(
        SRC_CD_TABLE_NAME,
        metadata,
        sa.Column('Src_Cd', sa.String(2), nullable=False, comment='A 2-digit code indicating type of data.'),
        sa.Column('SrcCd_Desc', sa.String(60), nullable=False, comment= 'Description of source code that identifies the type of nutrient data.'),
        sa.PrimaryKeyConstraint(*SRC_CD_KEYS)
    )

def _saveSourceCodesToSql(engine, df):
    df.set_index(SRC_CD_KEYS).to_sql(SRC_CD_TABLE_NAME, con=engine, if_exists='append')

DERIV_CD_TABLE_NAME="deriv_cd"
DERIV_CD_KEYS=['Deriv_Cd']

def _definedDerivationCodeTable(metadata):
    return sa.Table(
        DERIV_CD_TABLE_NAME,
        metadata,
        sa.Column('Deriv_Cd', sa.String(4), nullable=False, comment='Derivation Code.'),
        sa.Column('Deriv_Desc', sa.String(120), nullable=False, comment='Description of derivation code giving specific information on how the value was determined.'),
        sa.PrimaryKeyConstraint(*DERIV_CD_KEYS)
    )

def _saveDerivationCodesToSql(engine, df):
    df.set_index(DERIV_CD_KEYS).to_sql(DERIV_CD_TABLE_NAME, con=engine, if_exists='append')

NUT_DATA_TABLE_NAME="nut_data"
NUT_DATA_KEYS=['NDB_No', 'Nutr_No']

def _defineNutrientDataTable(metadata):
    return sa.Table(
        NUT_DATA_TABLE_NAME,
        metadata,
        sa.Column('NDB_No', sa.String(5), nullable=False, comment='Nutrient Databank number that uniquely identifies a food item. If this field is defined as numeric, the leading zero will be lost.'),
        sa.Column('Nutr_No', sa.String(3), nullable=False, comment='Unique 3-digit identifier code for a nutrient.'),
        sa.Column('Nutr_Val', sa.Numeric(10, 3), nullable=False, comment='Amount in 100 grams, edible portion.'),
        sa.Column('Num_Data_Pts', sa.Numeric(5, 0), nullable=False, comment='Number of data points is the number of analyses used to calculate the nutrient value. If the number of data points is 0, the value was calculated or imputed.'),
        sa.Column('Std_Error', sa.Numeric(8, 3), nullable=True, comment='Standard error of the mean. Null if cannot be calculated. The standard error is also not given if the number of data points is less than three.'),
        sa.Column('Src_Cd', sa.String(2), nullable=False, comment='Code indicating type of data.'),
        sa.Column('Deriv_Cd', sa.String(4), nullable=True, comment='Data Derivation Code giving specific information on how the value is determined. This field is populated only for items added or updated starting with SR14. This field may not be populated if older records were used in the calculation of the mean value.'),
        sa.Column('Ref_NDB_No', sa.String(5), nullable=True, comment='NDB number of the item used to calculate a missing value. Populated only for items added or updated starting with SR14.'),
        sa.Column('Add_Nutr_Mark', sa.String(1), nullable=True, comment='Indicates a vitamin or mineral added for fortification or enrichment. This field is populated for ready-toeat breakfast cereals and many brand-name hot cereals in food group 08.'),
        sa.Column('Num_Studies', sa.Numeric(2, 0), nullable=True, comment='Number of studies.'),
        sa.Column('Min', sa.Numeric(10, 3), nullable=True, comment='Minimum value.'),
        sa.Column('Max', sa.Numeric(10, 3), nullable=True, comment='Maximum value.'),
        sa.Column('DF', sa.Numeric(4, 0), nullable=True, comment='Degrees of freedom.'),
        sa.Column('Low_EB', sa.Numeric(10, 3), nullable=True, comment='Lower 95% error bound.'),
        sa.Column('Up_EB', sa.Numeric(10, 3), nullable=True, comment='Upper 95% error bound.'),
        sa.Column('Stat_cmt', sa.String(10), nullable=True, comment='Statistical comments. See definitions below.'),
        sa.Column('AddMod_Date', sa.String(10), nullable=True, comment='Indicates when a value was either added to the database or last modified.'),
        sa.Column('CC', sa.String(1), nullable=True, comment='Confidence Code indicating data quality, based on evaluation of sample plan, sample handling, analytical method, analytical quality control, and number of samples analyzed. Not included in this release, but is planned for future releases.'),
        sa.PrimaryKeyConstraint(*NUT_DATA_KEYS),
        sa.ForeignKeyConstraint(['NDB_No'], [FOOD_DES_TABLE_NAME + '.NDB_No']),
        sa.ForeignKeyConstraint(['Nutr_No'], [NUTR_DEF_TABLE_NAME + '.Nutr_No']),
        sa.ForeignKeyConstraint(['Src_Cd'], [SRC_CD_TABLE_NAME + '.Src_Cd']),
        sa.ForeignKeyConstraint(['Deriv_Cd'], [DERIV_CD_TABLE_NAME + '.Deriv_Cd']),
    )

def _saveNutrientDataToSql(engine, df):
    df.set_index(NUT_DATA_KEYS).to_sql(NUT_DATA_TABLE_NAME, con=engine, if_exists='append')

DATA_SRC_TABLE_NAME="data_src"
DATA_SRC_KEYS=['DataSrc_ID']

def _defineSourcesOfDataTable(metadata):
    return sa.Table(
        DATA_SRC_TABLE_NAME,
        metadata,
        sa.Column('DataSrc_ID', sa.String(6), nullable=False, comment='Unique ID identifying the reference/source.'),
        sa.Column('Authors', sa.String(255), nullable=True, comment='List of authors for a journal article or name of sponsoring organization for other documents.'),
        sa.Column('Title', sa.String(255), nullable=False, comment='Title of article or name of document, such as a report from a company or trade association.'),
        sa.Column('Year', sa.String(4), nullable=True, comment='Year article or document was published.'),
        sa.Column('Journal', sa.String(135), nullable=True, comment='Name of the journal in which the article was published.'),
        sa.Column('Vol_City', sa.String(16), nullable=True, comment='Volume number for journal articles, books, or reports; city where sponsoring organization is located.'),
        sa.Column('Issue_State', sa.String(5), nullable=True, comment='Issue number for journal article; State where the sponsoring organization is located.'),
        sa.Column('Start_Page', sa.String(5), nullable=True, comment='Starting page number of article/document.'),
        sa.Column('End_Page', sa.String(5), nullable=True, comment='Ending page number of article/document.'),
        sa.PrimaryKeyConstraint(*DATA_SRC_KEYS)
    )

def _saveSourcesOfDataToSql(engine, df):
    df.set_index(DATA_SRC_KEYS).to_sql(DATA_SRC_TABLE_NAME, con=engine, if_exists='append')

DATASRCLN_TABLE_NAME="datasrcln"
DATASRCLN_KEYS=['NDB_No', 'Nutr_No', 'DataSrc_ID']

def _defineDataSourceLinkTable(metadata):
    return sa.Table(
        DATASRCLN_TABLE_NAME,
        metadata,
        sa.Column('NDB_No', sa.String(5), nullable=False, comment='5-digit Nutrient Databank number that uniquely identifies a food item. If this field is defined as numeric, the leading zero will be lost.'),
        sa.Column('Nutr_No', sa.String(3), nullable=False, comment='Unique 3-digit identifier code for a nutrient.'),
        sa.Column('DataSrc_ID', sa.String(6), nullable=False, comment='Unique ID identifying the reference/source.'),
        sa.PrimaryKeyConstraint(*DATASRCLN_KEYS),
        sa.ForeignKeyConstraint(['DataSrc_ID'], [DATA_SRC_TABLE_NAME + '.DataSrc_ID']),
        sa.ForeignKeyConstraint(['NDB_No'], [FOOD_DES_TABLE_NAME + '.NDB_No']),
        sa.ForeignKeyConstraint(['Nutr_No'], [NUTR_DEF_TABLE_NAME + '.Nutr_No']),
        sa.ForeignKeyConstraint(['NDB_No', 'Nutr_No'], [NUT_DATA_TABLE_NAME + '.NDB_No', NUT_DATA_TABLE_NAME + '.Nutr_No'])
    )

def _saveDataSourceLinksToSql(engine, df):
    df.set_index(DATASRCLN_KEYS).to_sql(DATASRCLN_TABLE_NAME, con=engine, if_exists='append')

LANGDESC_TABLE_NAME="langdesc"
LANGDESC_KEYS=['Factor_Code']

def _defineLanguaLFactorDescriptionTable(metadata):
    return sa.Table(
        LANGDESC_TABLE_NAME,
        metadata,
        sa.Column('Factor_Code', sa.String(5), nullable=False, comment='The LanguaL factor from the Thesaurus. Only those codes used to factor the foods contained in the LanguaL Factor file are included in this file.'),
        sa.Column('Description', sa.String(140), nullable=False, comment='The description of the LanguaL Factor Code from the thesaurus.'),
        sa.PrimaryKeyConstraint(*LANGDESC_KEYS)
    )

def _saveLanguaLFactorDescriptionsToSql(engine, df):
    df.set_index(LANGDESC_KEYS).to_sql(LANGDESC_TABLE_NAME, con=engine, if_exists='append')

LANGUAL_TABLE_NAME="langual"
LANGUAL_KEYS=['NDB_No', 'Factor_Code']

def _defineLanguaLFactorTable(metadata):
    return sa.Table(
        LANGUAL_TABLE_NAME,
        metadata,
        sa.Column('NDB_No', sa.String(5), nullable=False, comment='5-digit Nutrient Databank number that uniquely identifies a food item. If this field is defined as numeric, the leading zero will be lost.'),
        sa.Column('Factor_Code', sa.String(5), nullable=False, comment='The LanguaL factor from the Thesaurus.'),
        sa.PrimaryKeyConstraint(*LANGUAL_KEYS),
        sa.ForeignKeyConstraint(['NDB_No'], [FOOD_DES_TABLE_NAME + '.NDB_No']),
        sa.ForeignKeyConstraint(['Factor_Code'], [LANGDESC_TABLE_NAME + '.Factor_Code'])
    )

def _saveLanguaLFactorsToSql(engine, df):
    df.set_index(LANGUAL_KEYS).to_sql(LANGUAL_TABLE_NAME, con=engine, if_exists='append')

FOOTNOTE_TABLE_NAME="footnote"

def _defineFootnoteTable(metadata):
    return sa.Table(
        FOOTNOTE_TABLE_NAME,
        metadata,
        #sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('NDB_No', sa.String(5), nullable=False, comment='5-digit Nutrient Databank number that uniquely identifies a food item. If this field is defined as numeric, the leading zero will be lost.'),
        sa.Column('Footnt_No', sa.String(4), nullable=False, comment='Sequence number. If a given footnote applies to more than one nutrient number, the same footnote number is used. As a result, this file cannot be indexed and there is no primary key.'),
        sa.Column('Footnt_Typ', sa.String(1), nullable=False, comment='Type of footnote: D = footnote adding information to the food description; M = footnote adding information to measure description; N = footnote providing additional information on a nutrient value. If the Footnt_typ = N, the Nutr_No will also be filled in.'),
        sa.Column('Nutr_No', sa.String(3), nullable=True, comment='Unique 3-digit identifier code for a nutrient to which footnote applies.'),
        sa.Column('Footnt_Txt', sa.String(200), nullable=False, comment='Footnote text.'),
        sa.ForeignKeyConstraint(['NDB_No'], [FOOD_DES_TABLE_NAME + '.NDB_No']),
        sa.ForeignKeyConstraint(['Nutr_No'], [NUTR_DEF_TABLE_NAME + '.Nutr_No']),
        #sa.ForeignKeyConstraint(['NDB_No', 'Nutr_No'], [NUT_DATA_TABLE_NAME + '.NDB_No', NUT_DATA_TABLE_NAME + '.Nutr_No'])
    )

def _saveFootnotesToSql(engine, df):
    df.to_sql(FOOTNOTE_TABLE_NAME, con=engine, if_exists='append', index=False)

def loadData():
    engine = sa.create_engine('mysql+mysqlconnector://admin:trustno1@localhost/ndb?charset=utf8', encoding='utf-8')

    metadata = sa.MetaData(bind=engine)
    metadata.reflect()
    
    if FD_GROUP_TABLE_NAME not in metadata.tables:
        _defineFoodGroupTable(metadata)
    if FOOD_DES_TABLE_NAME not in metadata.tables:
        _defineFoodDescriptionTable(metadata)
    if WEIGHTS_TABLE_NAME not in metadata.tables:
        _defineWeightsTable(metadata)
    if NUTR_DEF_TABLE_NAME not in metadata.tables:
        _defineNutrientDefinitionTable(metadata)
    if SRC_CD_TABLE_NAME not in metadata.tables:
        _defineSourceCodeTable(metadata)
    if DERIV_CD_TABLE_NAME not in metadata.tables:
        _definedDerivationCodeTable(metadata)
    if NUT_DATA_TABLE_NAME not in metadata.tables:
        _defineNutrientDataTable(metadata)
    if DATA_SRC_TABLE_NAME not in metadata.tables:
        _defineSourcesOfDataTable(metadata)
    if DATASRCLN_TABLE_NAME not in metadata.tables:
        _defineDataSourceLinkTable(metadata)
    if LANGDESC_TABLE_NAME not in metadata.tables:
        _defineLanguaLFactorDescriptionTable(metadata)
    if LANGUAL_TABLE_NAME not in metadata.tables:
        _defineLanguaLFactorTable(metadata)
    if FOOTNOTE_TABLE_NAME not in metadata.tables:
        _defineFootnoteTable(metadata)

    metadata.create_all()

    folder = os.path.join(os.path.dirname(__file__), 'sr28asc')

    food_groups = pd.read_csv(
        os.path.join(folder, "FD_GROUP.txt"),
        sep='^',
        quotechar='~',
        header=None,
        encoding='iso-8859-1', 
        names=['FdGrp_Cd', 'FdGrp_Desc'],
        dtype={'FdGrp_Cd': np.object, 'FdGrp_Desc': np.object})
    _saveFoodGroupsToSql(engine, food_groups)

    food_descriptions = pd.read_csv(
        os.path.join(folder, "FOOD_DES.txt"), 
        sep='^', 
        quotechar='~', 
        true_values='Y',
        false_values='N',
        header=None, 
        encoding='iso-8859-1',
        names=['NDB_No', 'FdGrp_Cd', 'Long_Desc', 'Shrt_Desc', 'ComName', 'ManufacName', 'Survey', 'Ref_desc', 'Refuse', 'SciName', 'N_Factor', 'Pro_Factor', 'Fat_Factor', 'CHO_Factor'], 
        dtype={
            'NDB_No': np.object, 
            'FdGrp_Cd': np.object, 
            'Long_Desc': np.object, 
            'Shrt_Desc': np.object, 
            'ComName': np.object, 
            'ManufacName': np.object, 
            'Survey': np.bool, 
            'Ref_desc': np.object, 
            'Refuse': np.float64, 
            'SciName': np.object, 
            'N_Factor': np.float64, 
            'Pro_Factor': np.float64, 
            'Fat_Factor': np.float64, 
            'CHO_Factor': np.float64})
    _saveFoodDescriptionsToSql(engine, food_descriptions)

    weights = pd.read_csv(
        os.path.join(folder, "WEIGHT.txt"),
        sep='^',
        quotechar='~',
        header=None,
        encoding='iso-8859-1',
        names=['NDB_No', 'Seq', 'Amount', 'Msre_Desc', 'Gm_Wgt', 'Num_Data_Pts', 'Std_Dev'],
        dtype={'NDB_No': np.object, 'Seq': np.object, 'Amount': np.float64, 'Msre_Desc': np.object, 'Gm_Wgt': np.float64, 'Num_Data_Pts': np.float64, 'Std_Dev': np.float64})
    _saveWeightsToSql(engine, weights)

    nutr_defs = pd.read_csv(
        os.path.join(folder, "NUTR_DEF.txt"), 
        sep='^', 
        quotechar='~', 
        true_values='Y',
        false_values='N',
        header=None, 
        encoding='iso-8859-1', 
        names=['Nutr_No', 'Units', 'Tagname', 'NutrDesc', 'Num_Dec', 'SR_Order'],
        dtype={'Nutr_No': np.object, 'Units': np.object, 'Tagname': np.object, 'NutrDesc': np.object, 'Num_Dec': np.float64, 'SR_Order': np.float64})
    _saveNutrientDefinitionsToSql(engine, nutr_defs)

    source_codes = pd.read_csv(
        os.path.join(folder, "SRC_CD.txt"), 
        sep='^', 
        quotechar='~', 
        true_values='Y',
        false_values='N',
        header=None, 
        encoding='iso-8859-1', 
        names=['Src_Cd', 'SrcCd_Desc'],
        dtype={'Src_Cd': np.object, 'SrcCd_Desc': np.object})
    _saveSourceCodesToSql(engine, source_codes)

    derivation_codes = pd.read_csv(
        os.path.join(folder, "DERIV_CD.txt"), 
        sep='^', 
        quotechar='~', 
        true_values='Y',
        false_values='N',
        header=None, 
        encoding='iso-8859-1', 
        names=['Deriv_Cd', 'Deriv_Desc'],
        dtype={'Deriv_Cd': np.object, 'Deriv_Desc': np.object})
    _saveDerivationCodesToSql(engine, derivation_codes)

    nutrient_data = pd.read_csv(
        os.path.join(folder, "NUT_DATA.txt"), 
        sep='^', 
        quotechar='~', 
        true_values='Y',
        false_values='N',
        header=None, 
        encoding='iso-8859-1', 
        names=['NDB_No', 'Nutr_No', 'Nutr_Val', 'Num_Data_Pts', 'Std_Error', 'Src_Cd', 'Deriv_Cd', 'Ref_NDB_No', 'Add_Nutr_Mark', 'Num_Studies', 'Min', 'Max', 'DF', 'Low_EB', 'Up_EB', 'Stat_cmt', 'AddMod_Date', 'CC'],
        dtype={
            'NDB_No': np.object, 
            'Nutr_No': np.object, 
            'Nutr_Val': np.float64, 
            'Num_Data_Pts': np.float64, 
            'Std_Error': np.float64, 
            'Src_Cd': np.object, 
            'Deriv_Cd': np.object, 
            'Ref_NDB_No': np.object, 
            'Add_Nutr_Mark': np.object, 
            'Num_Studies': np.float64, 
            'Min': np.float64, 
            'Max': np.float64, 
            'DF': np.float64, 
            'Low_EB': np.float64, 
            'Up_EB': np.float64, 
            'Stat_cmt': np.object, 
            'AddMod_Date': np.object, 
            'CC': np.object})
    _saveNutrientDataToSql(engine, nutrient_data)

    sources_of_data = pd.read_csv(
        os.path.join(folder, "DATA_SRC.txt"), 
        sep='^', 
        quotechar='~', 
        true_values='Y',
        false_values='N',
        header=None, 
        encoding='iso-8859-1', 
        names=['DataSrc_ID', 'Authors', 'Title', 'Year', 'Journal', 'Vol_City', 'Issue_State', 'Start_Page', 'End_Page'],
        dtype={
            'DataSrc_ID': np.object, 
            'Authors': np.object, 
            'Title': np.object, 
            'Year': np.object, 
            'Journal': np.object, 
            'Vol_City': np.object, 
            'Issue_State': np.object, 
            'Start_Page': np.object, 
            'End_Page': np.object})
    _saveSourcesOfDataToSql(engine, sources_of_data)

    data_source_links = pd.read_csv(
        os.path.join(folder, "DATSRCLN.txt"),
        sep='^', 
        quotechar='~', 
        true_values='Y',
        false_values='N',
        header=None, 
        encoding='iso-8859-1', 
        names=['NDB_No', 'Nutr_No', 'DataSrc_ID'],
        dtype={'NDB_No': np.object, 'Nutr_No': np.object, 'DataSrc_ID': np.object})
    _saveDataSourceLinksToSql(engine, data_source_links)

    langual_factor_descriptions = pd.read_csv(
        os.path.join(folder, "LANGDESC.txt"), 
        sep='^', 
        quotechar='~', 
        true_values='Y',
        false_values='N',
        header=None, 
        encoding='iso-8859-1', 
        names=['Factor_Code', 'Description'],
        dtype={'Factor_Code': np.object, 'Description': np.object})
    _saveLanguaLFactorDescriptionsToSql(engine, langual_factor_descriptions)

    langual_factors = pd.read_csv(
        os.path.join(folder, "LANGUAL.txt"), 
        sep='^', 
        quotechar='~', 
        true_values='Y',
        false_values='N',
        header=None, 
        encoding='iso-8859-1', 
        names=['NDB_No', 'Factor_Code'],
        dtype={'NDB_No': np.object, 'Factor_Code': np.object})
    _saveLanguaLFactorsToSql(engine, langual_factors)

    footnotes = pd.read_csv(
        os.path.join(folder, "FOOTNOTE.txt"), 
        sep='^', 
        quotechar='~', 
        true_values='Y',
        false_values='N',
        header=None, 
        encoding='iso-8859-1', 
        names=['NDB_No', 'Footnt_No', 'Footnt_Typ', 'Nutr_No', 'Footnt_Txt'],
        dtype={'NDB_No': np.object, 'Footnt_No': np.object, 'Footnt_Typ': np.object, 'Nutr_No': np.object, 'Footnt_Txt': np.object})
    _saveFootnotesToSql(engine, footnotes)

    print("Done")

if __name__ == "__main__":
    loadData()

