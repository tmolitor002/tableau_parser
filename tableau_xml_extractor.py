import pandas as pd
import xml.etree.ElementTree as ET
import zipfile
# import sys
import os.path

class TableauWorkbook():

    def __init__(self, filePath):
        self.filepath = os.path.normpath(filePath)
        self.filename = os.path.basename(filePath)
        # self.workbookname = self._get_workbook_name()
        self.xmlRoot = self._get_xml_root()
        self.parameters = self._get_parameters()
        self.calculations = self._get_tableau_calculations()
        # self.datasources = self._get_data_sources()

    def _get_xml_root(self):
        filePath = self.filepath
        if filePath[-4:]=='.twb':
            root = ET.parse(filePath).getroot()
        elif filePath[-4:]=='.xml':
            root = ET.parse(filePath).getroot()
        elif filePath[-5:]=='.twbx':
            with open(filePath, "rb") as binfile:
                twbx = zipfile.ZipFile(binfile)
                name = [w for w in twbx.namelist() if w.find(".twb") != -1][0]
                unzip = twbx.open(name)
                xml = ET.parse(unzip)
                xml.write(name[:-4] +".xml") #Writing corresponding xml file
                root = xml.getroot()
        else:
            print('Error: Only .twb, .twbx, or .xml files accepted.')
            print('Error: Skipping ' + self.filepath)
        return root
    
    def _get_parameters(self):
        '''To get parameters in a dataframe from the root element'''
        temp = []
        parameters = self.xmlRoot.findall("./datasources/datasource[@name='Parameters']/column")
        for element in parameters:
            temp.append({
                'File Name': self.filename,
                'File Path': self.filepath,
                'caption': element.get('caption'),
                'Data Type': element.get('datatype'),
                'Hidden Field Name': element.get('name'),
                'Default Values': element.get('value'),
                'param-domain-type': element.get('param-domain-type'),
                'Field Type': element.get('role'),
                'Data Category': element.get('type'),
                'members': self.find_members(element)
            })
        df = pd.DataFrame(temp)
        return df
    
    def _get_tableau_calculations(self):
        '''To get datasources in a dataframe from the root element'''
        temp = []
        datasources = self.xmlRoot.findall("./datasources/datasource")
        
        for datasource in datasources:
            calc = datasource.findall("./*calculation[@class='tableau']/..[@name]")
            for element in calc:
                temp.append({
                    'File Name': self.filename,
                    'File Path': self.filepath,
                    'Data Source': self.extract_alias_name(datasource),
                    'Tableau Field Name': self.extract_alias_name(element),
                    'Hidden Field Name': element.get('name'),
                    'Field Type': element.get('role'),
                    'Data Category': element.get('type'),
                    'Data Type': element.get('datatype'),
                    'Formula': element.find('./calculation').get('formula')
                })
        df = pd.DataFrame(temp)
        if len(df)==0: # if there are no calculations in dashboard)
            return df
        
        # Update calculation formula & add impacted calculations
        temp_df = pd.DataFrame()
        for ds in df['Data Source'].unique():
            calcs_sub = df[df['Data Source']==ds]
            calcs_sub = self.update_calculation_formula(calcs_sub)
            calcs_sub = self.add_impacted_fields(calcs_sub)
            temp_df = pd.concat([temp_df, calcs_sub])

        df = temp_df.reset_index(drop=True)
        return df
    
    # def _get_workbook_name(self):
    #     df = []
    #     workbooks = self.xmlRoot.findall("/workbook/repository-location")
    #     for element in workbook:
    #         df.append({
    #             'Workbook Name': element.get('id'),
    #             'Site': element.get('site'),
    #             'Revision': element.get('revision')
    #         })
    #     return df

    def find_members(self, parameter):
        member = []
        members = parameter.findall("./members/member")
        for item in members:
            member.append(item.get('value'))
        return ",".join(member)

    def update_calculation_formula(self, calcs_sub):
        '''To update the formula field, to replace tableau identifiers with their user defined names'''
        search_dict = self.create_identifier_dict(calcs_sub)
        # search_dict.update(self.create_identifier_dict(self.parameters)) # not currently interested in parameters

        for i in range(len(calcs_sub)):
            calcs_sub = calcs_sub.reset_index(drop=True)
            cell = calcs_sub['Formula'][i]
            for key in list(search_dict.keys()):
                if key in cell:
                    cell = cell.replace(key, "[" +search_dict[key] + "]")
            calcs_sub['Formula'][i] = cell
        return calcs_sub

    def add_impacted_fields(self, calcs_sub):
        '''to Add a list of corresponding impacted calculations for each calculation'''
        calcs_sub['Child Formulas'] = pd.Series()
        for i in range(len(calcs_sub)):
            calcs_sub['Child Formulas'][i] = ""
            _caption = "[" + calcs_sub['caption'][i] + "]"
            for j in range(len(calcs_sub)):
                if _caption in calcs_sub['Formula'][j]:
                    calcs_sub['Child Formulas'][i] += ("," + calcs_sub['caption'][j] + "]")

            calcs_sub['Child Formulas'][i] = calcs_sub['Child Formulas'][i][1:]

        return calcs_sub
    
    def output_to_excel(self): # Comeback and revist, may want to do this in main
        '''To write to multiple sheets in excel using ExcelWriter'''
        with pd.ExcelWriter("./Workbook Details.xlsx") as writer:
            self.calculations.to_excel(writer, sheet_name="Calculated Fields", index=False)

    def create_identifier_dict(self,df):
        df = df[['name','caption']]
        df.index = df['name']
        df.drop(columns='name', inplace=True)
        dictn = df.to_dict()['caption']
        return dictn

    def extract_alias_name(self, element):
        if element.get('caption') is None:
            element = element.get('name')
            val = element.replace("[","").replace("]","")
            return val
        else:
            return element.get('caption')