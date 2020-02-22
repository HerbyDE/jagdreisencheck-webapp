#!/usr/bin/python -u
import sys
import os
import django
import xlrd
import simplejson
from collections import OrderedDict


def convert_xlsx_to_json(path):

    wb = xlrd.open_workbook("/Users/herbertwoisetschlager/OneDrive/Jagdreisencheck/04_IT/06_Uploads/Scrapper_Output/20190528_HunterMeetsHunter.xlsx")
    
    for sheet_index in range(wb.nsheets):
        sh = wb.sheet_by_index(sheet_index)
        rows_list = []
        col_names = []
    
        if sh.nrows == 0:
                continue
    
        attr_list = sh.row_values(0)
        map_db_keys = [
            ('web_id', "Web-ID"),
            ('url', 'URL'),
            ('location', 'Ort:'),
            ('company', 'von:'),
            ('hunting_time', 'Jagdzeit:'),
            ('available_hunting_types', 'Jagdarten:'),
            ('amenities', 'Ausstattung:'),
            ('staff_languages', 'Sprachen:'),
            ('airport_transfer', 'Abholung:'),
            ('available_accommodation_types', 'Unterkunft:'),
            ('game', 'Wildarten:')
        ]
    
        for i, val in enumerate(attr_list):
            col = 0
            for k, v in map_db_keys:
                if val == v:
                    col_names.append((i, k))
                    col += 1
    
        for rownum in range(1, sh.nrows):
            row_values = sh.row_values(rownum)
            row_dict = OrderedDict()
            
            for i, k in col_names:
                
                if type(row_values[i]) == str:
                    pcs = row_values[i].split(", ")
                    li = []
                    for pc in pcs:
                        if len(pc) > 0:
                            if pc == "Ja" or pc == "Yes":
                                li.append("True")
                            elif pc == "Nein" or pc == "No":
                                li.append("False")
                            else:
                                li.append(pc.replace(",", "").strip())
                    row_dict[k] = li
                    
                else:
                    row_dict[k] = str(int(row_values[i]))
                    
            
    
            rows_list.append(row_dict)
            
        return simplejson.dumps(rows_list)
    
    
def preprocess_json(data):
    
    data = simplejson.loads(data)
    output = []
    
    for row in data:
        
        # Add required fields that were not available on the peer page.
        row['private_parking'] = None
        row['rifle_rentals'] = None
        row['family_offers'] = None
        row['alternative_activities'] = None
        row['interpreter_at_site'] = None
        row['wireless_coverage'] = None
        row['broadband_internet'] = None
        
        # Process location:
        splitter = row['location'][0].split("/")
        row['country'] = splitter[0].strip()
        row['region'] = splitter[1].strip()
        row['location'] = None
        
        # Process hunting time
        splitter = row['hunting_time'][0].split("-")
        row['hunting_start_time'] = splitter[0].strip().split(" ")[1]
        row['hunting_end_time'] = splitter[1].strip().split(" ")[1]
        row['hunting_time'] = None
        
        if row['hunting_start_time'] == 'Jänner':
            row['hunting_start_time'] = 'Januar'
            
        if row['hunting_end_time'] == 'Jänner':
            row['hunting_end_time'] = 'Januar'
        
        for k in row.keys():
            if (row[k] is not None and len(row[k]) == 1 and not k == 'game' and not k == 'staff_languages'
                    and not k == 'available_accommodation_types'):
                row[k] = row[k][0]
        
    for row in data:
        if "Deutsch" in row['staff_languages']:
            output.append(row)
        
    data = simplejson.dumps(output)
        
    return data
        
        
if __name__ == '__main__':
    l = convert_xlsx_to_json("")
    p = preprocess_json(l)
    # upload_trip(p)
    print(p)
