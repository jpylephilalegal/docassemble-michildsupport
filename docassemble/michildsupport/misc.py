from bs4 import BeautifulSoup as Soup
import re
import json
import sys
import shutil
import tempfile
import os
import subprocess
from pathlib import Path

from docassemble.base.util import log, path_and_mimetype, validation_error, DADict, DAList, Individual, value, force_ask, space_to_underscore

__all__ = ['run_automation', 'noquote', 'number_with_max', 'retirement_index_increment', 'ParentDict', 'ChildrenList']

class ParentDict(DADict):
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.object_type = Individual
        self.auto_gather = False

class ChildrenList(DAList):
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.object_type = Individual
        self.ask_number = True
    def hook_on_gather(self):
        if 'C' in value('child_support_group') and not any(child.lives_with_non_parent_custodian for child in self.elements):
            force_ask('no_child_with_guardian')
    def hook_after_gather(self):
        self.sort(key=lambda y: y.birthdate, reverse=True)

def retirement_index_increment(parent):
    if parent.tax_method == 'estimated':
        for income_source in parent.income_sources:
            if income_source.type == 'Employer Wages' and income_source.must_contribute_to_retirement and income_source.mandatory_percentage > 0:
                return 1
    return 0

def number_with_max(number, maximum):
    if number >= maximum:
        return str(maximum) + '+'
    return str(number)

def noquote(text):
    if re.search(r'[^A-Za-z\' 0-9\_\-\n\r]', text):
        raise validation_error("You are only allowed to type characters A-Z, a-z, 0-9, and -.")
    return True

def run_automation(feature_file, html_file, png_file, json_file, base_name):
    base_name = space_to_underscore(base_name)
    try:
        with tempfile.TemporaryDirectory(prefix='datemp') as temp_directory:
            output_file = os.path.join(temp_directory, 'output.html')
            output_png = os.path.join(temp_directory, 'output.png')
            features_directory = shutil.copytree(path_and_mimetype('data/sources/features')[0], os.path.join(temp_directory, 'features'))
            shutil.copyfile(feature_file, os.path.join(features_directory, 'calculate.feature'))
            Path(os.path.join(features_directory, '__init__.py')).touch()
            Path(os.path.join(features_directory, 'steps', '__init__.py')).touch()
            output = ''
            with open(feature_file, encoding='utf-8') as x:
                output += x.read()
            try:
                commands = ["aloe", "--stop", "--verbosity=3", "features/calculate.feature"]
                output += "\n\n" + ' '.join(commands) + "\n"
                #output += subprocess.check_output(["ls", "-lR"], cwd=temp_directory, stderr=subprocess.STDOUT).decode()
                output += subprocess.check_output(commands, cwd=temp_directory, stderr=subprocess.STDOUT).decode()
                success = True
            except subprocess.CalledProcessError as err:
                output += err.output.decode()
                success = False
            if success:
                if os.path.isfile(output_file):
                    html_file.initialize(filename=base_name + '.html')
                    html_file.copy_into(output_file)
                    html_file.commit()
                else:
                    success = False
                    output += "\nFile not found after process completed.\n"
                if os.path.isfile(output_png):
                    png_file.initialize(filename=base_name + '.png')
                    png_file.copy_into(output_png)
                    png_file.commit()
                else:
                    success = False
                    output += "\nPNG file not found after process completed.\n"
    except Exception as err:
        success = False
        output = err.__class__.__name__ + ": " + str(err)
    if success:
        try:
            output_data = extract_data(html_file.path())
            json_file.initialize(filename=base_name + '.json')
            json_file.write(json.dumps(output_data, indent=2))
            json_file.commit()
        except Exception as err:
            success = False
            output += err.__class__.__name__ + ": " + str(err)
            output_data = {"error": err.__class__.__name__, "message": str(err)}
    else:
        output_data = {}    
    return success, output, output_data

def process_table(table):
    result = dict()
    result['title'] = table.get('title', None)
    result['columns'] = []
    result['rows'] = []
    result['footer'] = []
    for head in table.find_all('thead', recursive=False):
        result['columns'].append(head.get_text().strip())
    for body in table.find_all('tbody', recursive=False):
        for row in body.find_all('tr', recursive=False):
            output_row = []
            item = list()
            for col in row.find_all('td', recursive=False):
                output_row.append(fixup(col))
            result['rows'].append(output_row)
    for foot in table.find_all('tfoot', recursive=False):
        result['footer'].append(foot.get_text().strip())
    return result    

def fixup(elem):
    children = [item for item in elem.find_all(recursive=False) if item.name != 'br']
    if len(children) == 1:
        orig_elem = elem
        elem = children[0]
        #log("kids1: found a " + elem.name + " with " + repr(elem.get_text()))
        if elem.name == 'output':
            text = orig_elem.get_text().strip()
        elif elem.name == 'div':
            found = False
            tables = list()
            for table in elem.find_all('table'):
                found = True
                tables.append(process_table(table))
#                for head in table.find_all('thead', recursive=False):
#                    tables.append(head.get_text().strip())
            if found:
                return tables
            text = orig_elem.get_text().strip()
        elif elem.name == 'table':
            #tables = list()
            #for head in elem.find_all('thead', recursive=False):
            #    tables.append(head.get_text().strip())
            #return tables
            return process_table(elem)
        elif elem.name == 'input':
            text = elem.get('value') 
        else:
            #log("doing get text and strip")
            text = elem.text.strip()
            #log("doing elem is" + repr(text))
            text = re.sub(r'<br/?>', ' ', text)
    elif len(children) == 2 and children[0].name == 'table' and children[1].name == 'table':
        return [process_table(children[0]), process_table(children[1])]
    elif len(children) == 2 and children[0].name == 'a' and children[1].name == 'label':
        text = children[1].get_text().strip()
    elif len(children) == 2 and children[0].name == 'output' and children[1].name == 'output':
        text = children[0].get_text().strip() + " " + children[1].get_text().strip()
    elif len(children) == 3 and children[0].name == 'div' and children[1].name == 'div' and children[2].name == 'div':
        #log("Triple div first kid is " + repr(str(children[0])))
        text = children[0].get_text().strip() + " " + children[1].get_text().strip() + " " + children[2].get_text().strip()
        #log("Triple div Got " + repr(text))
    elif len(children) == 2 and children[0].name == 'div' and children[1].name == 'div':
        text = children[0].get_text().strip() + " " + children[1].get_text().strip()
    elif len(children) == 2 and children[0].name == 'strong' and children[1].name == 'strong':
        text = children[0].get_text().strip() + " " + children[1].get_text().strip()
    elif len(children) == 2 and children[0].name == 'p' and children[1].name == 'p':
        text = children[0].get_text().strip() + " " + children[1].get_text().strip()
    elif len(children) == 2 and children[0].name == 'div' and children[1].name == 'p':
        text = children[1].get_text().strip()
    else:
        #log("found a " + elem.name + " with " + repr(elem.get_text()))
        #log("kids is " + ";".join(repr(item.name) for item in children))
        text = elem.decode_contents().strip()
        #log("elem is" + repr(text))
        text = re.sub(r'<br/?>', ' ', text)
    if not isinstance(text, str):
        return text
    text = re.sub(r' ', ' ', text)
    text = re.sub(r'  +', ' ', text)
    text = re.sub(r'\n\t+', ' ', text)
    text = text.strip()
    m = re.search(r'^\$([0-9]+\.[0-9][0-9])$', text)
    if m:
        text = float(m.group(1))
    return text

def nulltruefalse(item):
    if isinstance(item, str):
        if item in ('false', 'No'):
            return False
        if item in ('true', 'Yes'):
            return True
        if item in ('-', ''):
            return None
        if re.search(r'^\-?[0-9]+$', item):
            try:
                return int(item)
            except:
                pass
        if '.' in item and re.search(r'^\-?[0-9\.]+$', item):
            try:
                return float(item)
            except:
                pass
        if re.search(r'^[0-9\.]+\%$', item):
            try:
                return float(item[0:-1])/100.0
            except:
                pass
    return item

def get_amount_potential(text):
    if not isinstance(text, str):
        return (text, False)
    if '(PC)' in text:
        potential = True
    else:
        potential = False
    m = re.search(r'^\$([0-9\.]+)', text)
    if m:
        try:
            text = float(m.group(1))
        except:
            pass
    return (text, potential)

def extract_data(filename):
    results = {"parts": [], "hidden": {}, "summary": []}
    with open(filename) as fp:
        s = Soup(fp.read(), "html.parser")
        for inp in s.select('input[type="hidden"]'):
            results['hidden'][inp.get('id') or inp.get('name')] = inp.get('value')
        for i in range(3):
            for div in s.select('#showResult' + str(i)):
                link_text = div.get_text().strip()
                link_text = re.sub(r'\s+', ' ', link_text)
                link_text = re.sub(r'Show Result [0-9]+: ', '', link_text)
                results['summary'].append(link_text)
            for div in s.select('#paymentRelationship' + str(i)):
                result = {}
                for table in div.find_all('table', recursive=False):
                    heading = None
                    for head in table.find_all('thead', recursive=False):
                        heading = head.get_text().strip()
                    if not heading:
                        raise Exception("Table has no heading")
                    heading = re.sub(r'^Section:\s*', '', heading)
                    result[heading] = []
                    for body in table.find_all('tbody', recursive=False):
                        for row in body.find_all('tr', recursive=False):
                            item = list()
                            for col in row.find_all('td', recursive=False):
                                item.append(fixup(col))
                            result[heading].append(item)
                results['parts'].append(result)
    #log("Raw:")
    #log(json.dumps(results, indent=2))
    main_output = {'results': [], 'information': {}, 'summaries': []}
    for part in results['parts']:
        output = dict()
        for item in ('General Information', 'Eliminate Ordinary Medical Expenses', 'Calculation Results', 'Children', 'Financial', 'Base Support Calculation', 'Child Care'):
            if item not in part:
                raise Exception(item + " not found")
        for item in part['General Information']:
            if item[0] == 'Court Case Number' and len(item) >= 4:
                output['Court Case Number'] = item[1]
                if item[2] == 'Court Case County':
                    output['Court Case County'] = item[3]
            elif item[0] == 'Calculation Parties' and len(item) >= 4:
                output['Calculation Parties'] = [item[1], item[3]]
            elif item[0] == 'Description' and len(item) > 1:
                output['Description'] = item[1]
            elif item[0] == 'Michigan Child Support Formula Year' and len(item) >= 6:
                output[item[0]] = item[1]
                output[item[2]] = item[3]
                output[item[4]] = item[5]
        headers = None
        for item in part['Eliminate Ordinary Medical Expenses']:
            if item[0] == "":
                headers = item[1:]
                break
        if headers is None:
            raise Exception("Could not find header row for Eliminate Ordinary Medical Expenses")
        subout = dict()
        for item in part['Eliminate Ordinary Medical Expenses']:
            if item[0] == "":
                continue
            if len(item) == 1 + len(headers):
                subsubout = dict()
                for i in range(len(headers)):
                    subsubout[headers[i]] = nulltruefalse(item[i + 1])
                subout[item[0]] = subsubout
            if len(item) == 2 and item[0] == 'Select Reason for Eliminating the Ordinary Medical Expense(s):':
                subout[item[0]] = item[1]
        output['Eliminate Ordinary Medical Expenses'] = subout
        headers = None
        for item in part['Calculation Results']:
            if item[0] == "":
                headers = item[1:]
                break
        if headers is None:
            raise Exception("Could not find header row for Calculation Results")
        subout = dict()
        for item in part['Calculation Results']:
            if item[0] == "":
                continue
            if len(item) == 1 + len(headers):
                subsubout = dict()
                for i in range(len(headers)):
                    subsubout[headers[i]] = nulltruefalse(item[i + 1])
                subout[item[0]] = subsubout
            if len(item) == 2 and item[0] == 'Select Reason for Eliminating the Ordinary Medical Expense(s):':
                subout[item[0]] = item[1]
        output['Calculation Results'] = subout
        headers = None
        for item in part['Children']:
            if item[0] == "Children's Overnights Spent Per Year":
                headers = item[1:]
                break
        if headers is None:
            raise Exception("Could not find header row for Children")
        subout = dict()
        overnights = dict()
        for item in part['Children']:
            if item[0] == "Children's Overnights Spent Per Year":
                continue
            if len(item) == 1 + len(headers):
                subsubout = dict()
                for i in range(len(headers)):
                    subsubout[headers[i]] = nulltruefalse(item[i + 1])
                if item[0] in ('Additional Children from Other Relationships', 'Child Support Children in Other Payment Relationships', 'Total Other Children', 'Income Adjustment Percentage Multiplier'):
                    subout[item[0]] = subsubout
                else:
                    for i in range(len(headers)):
                        if headers[i] not in overnights:
                            overnights[headers[i]] = dict()
                        overnights[headers[i]][item[0]] = nulltruefalse(item[i + 1])
        subout["Children's Overnights Spent Per Year"] = overnights
        output["Children"] = subout
        subout = dict(notes=list())
        headers = None
        for item in part['Financial']:
            if item[0] == "See 2021 MCSF 2.01":
                headers = item[1:]
                break
        if headers is None:
            raise Exception("Could not find header row for Financial")
        for item in part['Financial']:
            if len(item) > 0 and isinstance(item[0], list):
                if len(item[0]) > len(headers):
                    raise Exception("Unrecognized row of tables in Financial section. Expected " + str(len(headers)) + " and got " + str(len(item[0])) + " where content is " + repr(item[0]) + " and headers are " + repr(headers))
                for i in range(len(headers)):
                    if i >= len(item[0]):
                        continue
                    table = item[0][i]
                    if not isinstance(table, dict) or 'title' not in table or 'columns' not in table or 'rows' not in table:
                        raise Exception("Unrecognized table " + repr(table) + " in Financial section")
                    table_title = re.sub(r'^Party [0-9]+ ', '', table['title'])
                    if table_title not in subout:
                        subout[table_title] = dict()
                    subsubout = dict()
                    for subitem in table['rows']:
                        if not len(subitem) == 2:
                            raise Exception("Unrecognized row in table in Financial section")
                        subsubout[subitem[0]] = subitem[1]
                    subout[table_title][headers[i]] = subsubout
            elif len(item) == 1 and isinstance(item[0], str):
                subout['notes'].append(item[0])
            elif len(item) == 2:
                subout[item[0]] = item[1]
            elif len(item) == 1 + len(headers):
                if item[0] in ("See 2021 MCSF 2.01", "Additional Deductions"):
                    continue
                subsubout = dict()
                for i in range(len(headers)):
                    subsubout[headers[i]] = nulltruefalse(item[i + 1])
                label = item[0]
                label = re.sub(r' See 2021 MCSF 2.01', '', item[0])
                subout[label] = subsubout
        output["Financial"] = subout
        subout = dict()
        headers = None
        for item in part['Base Support Calculation']:
            if item[0] == "See 2021 MCSF 3.02(A)":
                headers = item[1:]
                break
        if headers is None:
            raise Exception("Could not find header row for Base Support Calculation")
        for item in part['Base Support Calculation']:
            if not len(item) == 1 + len(headers):
                raise Exception("Unrecognized row in Base Support Calculation")
            if item[0] == "See 2021 MCSF 3.02(A)":
                continue
            subsubout = dict()
            for i in range(len(headers)):
                subsubout[headers[i]] = nulltruefalse(item[i + 1])
            subout[item[0]] = subsubout
        output["Base Support Calculation"] = subout
        subout = dict(notes=list())
        reimbursement_end_dates = list()
        headers = None
        for item in part['Child Care']:
            if len(item) and  item[0] == "See 2021 MCSF 3.06(C) and 2021 MCSF 3.06(D)":
                headers = item[1:]
                break
        if headers is None:
            raise Exception("Could not find header row for Child Care")
        for item in part['Child Care']:
            if len(item) > 0 and isinstance(item[0], list):
                if len(item[0]) != len(headers):
                    raise Exception("Unrecognized row of tables in Child Care section")
                for i in range(len(headers)):
                    table = item[0][i]
                    if not isinstance(table, dict) or 'title' not in table or 'columns' not in table or 'rows' not in table:
                        raise Exception("Unrecognized table " + repr(table) + " in Child Care section")
                    if len(table['rows']) == 1:
                        continue
                    table_title = re.sub(r'^Party [0-9]+ ', '', table['title'])
                    table_title = re.sub(r'Child Care Expense Information Table', 'Child Care Expenses Information Table', table_title)
                    if table_title not in subout:
                        subout[table_title] = dict()
                    subsubout = list()
                    for subitem in table['rows']:
                        if not len(subitem) == 2:
                            raise Exception("Unrecognized row in table in Child Care section")
                        if subitem[0] == 'Months':
                            if len(subsubout) == 0:
                                raise Exception("Unrecognized Months row in Child Care section")
                            subsubout[-1]['months'] = subitem[1]
                        else:
                            amount, is_potential = get_amount_potential(subitem[1])
                            subsubout.append({'child': subitem[0], 'amount': amount, 'potential': is_potential})
                    subout[table_title][headers[i]] = subsubout
            elif len(item) == 0:
                continue
            elif len(item) == 1 and isinstance(item[0], str):
                subout['notes'].append(item[0])
            elif len(item) == 2:
                reimbursement_end_dates.append({'child': item[0], 'date': item[1]})
            elif len(item) == 1 + len(headers):
                if item[0] == "See 2021 MCSF 3.06(C) and 2021 MCSF 3.06(D)":
                    continue
                subsubout = dict()
                for i in range(len(headers)):
                    subsubout[headers[i]] = nulltruefalse(item[i + 1])
                subout[item[0]] = subsubout
        subout["Reimbursement End Dates"] = reimbursement_end_dates
        output["Medical"] = subout
        subout = dict(notes=list())
        headers = None
        for item in part['Medical']:
            if len(item) and  item[0] == "See 2021 MCSF 3.05(C) See 2021 MCSF 3.04(B)":
                headers = item[1:]
                break
        if headers is None:
            raise Exception("Could not find header row for Medical")
        for item in part['Medical']:
            if len(item) > 0 and isinstance(item[0], list):
                if len(item[0]) != len(headers):
                    raise Exception("Unrecognized row of tables in Medical section")
                for i in range(len(headers)):
                    table = item[0][i]
                    if not isinstance(table, dict) or 'title' not in table or 'columns' not in table or 'rows' not in table:
                        raise Exception("Unrecognized table " + repr(table) + " in Medical section")
                    if len(table['rows']) == 1:
                        continue
                    table_title = re.sub(r'^Party [0-9]+ ', '', table['title'])
                    if table_title not in subout:
                        subout[table_title] = dict()
                    subsubout = list()
                    for subitem in table['rows']:
                        if not len(subitem) == 2:
                            raise Exception("Unrecognized row in table in Medical section")
                        subsubout.append({'child': subitem[0], 'amount': amount})
                    subout[table_title][headers[i]] = subsubout
                    if 'footer' in table:
                        subout[table_title + " Note"] = '\n'.join(table['footer'])
            elif len(item) == 0:
                continue
            elif len(item) == 1 and isinstance(item[0], str):
                subout['notes'].append(item[0])
            elif len(item) == 2:
                subout[item[0]] = item[1]
            elif len(item) == 1 + len(headers):
                if item[0] in ("See 2021 MCSF 3.05(C) See 2021 MCSF 3.04(B)", "Additional Out-of-pocket Medical Expenses Per Child"):
                    continue
                subsubout = dict()
                for i in range(len(headers)):
                    subsubout[headers[i]] = nulltruefalse(item[i + 1])
                subout[item[0]] = subsubout
        output["Medical"] = subout
        main_output['results'].append(output)
    for item, val in results['hidden'].items():
        main_output["information"][item] = nulltruefalse(val)
    for item in results['summary']:
        main_output['summaries'].append(item)
    return main_output

# if __name__ == "__main__":
#     filename = 'mi-results.html'
#     raw_data = extract_data('mi-results.html')
#     print("Final:")
#     print(json.dumps(raw_data, indent=2))

