import os
from xml.etree.ElementTree import ElementTree
import xml.etree.ElementTree as ET
import copy

#################################################################
#                   DATA PREPARATION SECTION
#################################################################

#represent all active projects in ukraine
ukraine_tree = ET.parse(os.path.dirname(os.path.abspath(__file__)) + '/data/actif/Ukraine_actives.xml')
ukraine_projects = ukraine_tree.getroot()

#represent all terminating projects since 01/01/2018
terminating_tree = ET.parse(os.path.dirname(os.path.abspath(__file__)) + '/data/terminating/all_terminating_from_2018_01_01.xml')
terminating_projects = terminating_tree.getroot()

#represent all active projects ( ukraine included )
active_tree = ET.parse(os.path.dirname(os.path.abspath(__file__)) + '/data/actif/all_actives.xml')
active_projects = active_tree.getroot()

#represent all closed projects since 01/01/2018
closed_tree = ET.parse(os.path.dirname(os.path.abspath(__file__)) + '/data/closed/all_closed_since_2018.xml')
closed_projects = closed_tree.getroot()

#################################################################
#                DATA ANALYSIS FUNCTIONS SECTION
#################################################################

#get the country contribution %
def getCountryContributionPercentageNormalized(project, country_contrib_str):

    if country_contrib_str == '':
        return 1.0
    
    countries = project.find('countries')
    contrib_str = ''
    
    for country in countries:
        if country_contrib_str.lower() in country.text.lower():
            contrib_str = country.text
            break

    if contrib_str == '':
        return 1.0 #100%
    else:
        contrib_perc_str = contrib_str.split(' ')
        contrib_perc_str = contrib_perc_str[len(contrib_perc_str)-1]
        contrib_perc_str = contrib_perc_str[:len(contrib_perc_str)-1]
        contrib_perc_str = contrib_perc_str.replace(',', '.')
        return float(contrib_perc_str) / 100.0
        
    

#sums all contribution for a given project list. Will ignore promises and only calculate "sent" transactions
def sumProjectsContributions(projects_list, country_contrib_str):
    proj_sum = 0;
    for project in projects_list.findall('project'):
        contrib_mult = getCountryContributionPercentageNormalized(project, country_contrib_str)
        for transaction in project.find('transactions').findall('transaction'):
            if transaction.get('transactionType') == "Déboursé":
                proj_sum += float(transaction.text) * contrib_mult
    return proj_sum

#search in a given project list by keyword. Can include or exluce "0$ money sent" projects
def findProjectsByKeyWord(projects_list, keyword, include_0_projects):
    found_projects = ET.Element("filtered_by_word_"+keyword)

    for project in projects_list.iter('project'):
        to_sum = ET.Element("to_sum")
        to_sum.append(project)
        
        if not include_0_projects and sumProjectsContributions(to_sum, '') == 0:
            continue;

        if keyword == '':
            found_projects.append(project)
            continue
        
        if keyword.lower() in getXMLString(project).lower():
            found_projects.append(project)
            continue;

    return found_projects

#sort the given project list by highest contribution engagement
def getProjectsSortedByHighestContribution(project_list):
    sorted_projects = ET.Element("sorted_by_highest_contribution")
    for project in sorted(project_list, key=lambda x: float(x.find('maximumContribution').text), reverse=True):
        sorted_projects.append(copy.deepcopy(project))
    return sorted_projects

#sort the given project list by lowest contribution engagement
def getProjectsSortedByLowestContribution(project_list):
    sorted_projects = ET.Element("sorted_by_lowest_contribution")
    for project in sorted(project_list, key=lambda x: float(x.find('maximumContribution').text), reverse=False):
        sorted_projects.append(copy.deepcopy(project))
    return sorted_projects

#return a list of transaction information for given project list
#can ignore or include contribution engagement
#can ignore or include 0$ transactions
def getAllTransactions(project_list, include_promises, include_0):
    transactions = []
    for project in project_list.findall('project'):
        for transaction in project.find('transactions').findall('transaction'):
            if include_promises is True and transaction.get('transactionType') == "Engagement":
                transactions.append({"transaction":transaction, "program_name": project.find('programName').text, "exec_partner": project.find('executingAgencyPartner').text})
            elif transaction.get('transactionType') == "Déboursé":
                if include_0:
                    transactions.append({"transaction":transaction, "program_name": project.find('programName').text, "exec_partner": project.find('executingAgencyPartner').text})
                elif transaction.text is not None and transaction.text != "" and transaction.text != "0":
                    transactions.append({"transaction":transaction, "amount":transaction.text, "program_name": project.find('programName').text, "exec_partner": project.find('executingAgencyPartner').text})
    return transactions

#return the number of total transactions for given project list
#can ignore or include contribution engagement
#can ignore or include 0$ transactions
def nbTransactions(project_list, include_promises, include_0):
    return len(getAllTransactions(project_list, include_promises, include_0))

#################################################################
#                   UTILITY FUNCTIONS SECTION
#################################################################
#returns the xml element as a readable string
def getXMLString(xml_element):
    return ET.tostring(xml_element, encoding='unicode')

#print some project information 
def outputProjectDescription(project, country_contrib_str, output_func):
    xml_root = ET.Element("to_sum")
    xml_root.append(project)

    output_func("****************************")
    output_func("Titre du programme : " + project.find('title').text)
    output_func("Montant debourser :" + str(sumProjectsContributions(xml_root, country_contrib_str)))
    output_func("Agence partenaire executant :" + project.find('executingAgencyPartner').text)
    output_func()
    output_func(project.find('description').text)
    output_func(getXMLString(project.find('countries')))
    output_func('****************************')

#output all given projects description
def outputAllProjectsDescriptions(project_list, country_contrib_str, output_func):
    for project in project_list.findall('project'):
        outputProjectDescription(project, output_func)
        
#utility function to return a statistic object for given project list
def getProjectsStats(project_list, country_contrib_str):
    stats = {}
    stats['nb_projects'] = str(len(project_list.findall('project')))
    stats['total_contrib'] = str(sumProjectsContributions(project_list, country_contrib_str))
    stats['nb_transactions'] = str(nbTransactions(project_list, True, False))
    stats['nb_transactions_sent'] = str(nbTransactions(project_list, False, False))
    stats['transactions'] = getAllTransactions(project_list, False, False)
    return stats

#output a transaction information
def outputTransaction(transaction, output_func):
    desc_str = "Date:" + transaction['transaction'].get("transactionDate")
    desc_str = desc_str + " | Amount:" + transaction["amount"]
    desc_str = desc_str + " | Program:" + transaction['program_name']
    desc_str = desc_str + " | Executive partner:" + transaction['exec_partner']
    output_func(desc_str)

#output all transactions information
def outputTransactions(transactions, output_func):
    for transaction in transactions:
        outputTransaction(transaction, output_func)

#takes a list of xml root with 'project' elements to merge them into a single root
def mergeXMLProjects(list_of_xml_roots):
    xml_root = ET.Element("merged_projects")
    for xml_projects in list_of_xml_roots:
        for project in xml_projects.findall('project'):
            xml_root.append(project)
    return xml_root

#returns a hash table of the project list and ensures there is no project duplicate
def hashProjectsRemoveDuplicates(xml_project_list):
    project_hash_table = {}
    for project in xml_project_list.findall('project'):
        project_hash_table[hash(getXMLString(project))] = project
    return project_hash_table

def getXMLRootProjectListFromHashTable(project_hash_table):
    xml_root = ET.Element("no_duplicate_projects")
    for hash_val in project_hash_table:
        xml_root.append(project_hash_table[hash_val])
    return xml_root

def removeProjectDuplicates(xml_project_list_root):
    return getXMLRootProjectListFromHashTable(hashProjectsRemoveDuplicates(xml_project_list_root))

def findProjectsByCountries(project_list, country_str):
    xml_root = ET.Element("found_by_country")
    for project in project_list:
        proj_countries = project.find('countries')
        for proj_country in proj_countries:
            if country_str.lower() in proj_country.text.lower():
                xml_root.append(project)

    return xml_root

def ensureDirectoryExists(directory_name):
    os.makedirs(directory_name, exist_ok=True)

def writeStatsToFile(stats, dirname, filename, keyword):
    directory_name = os.path.join(os.path.dirname(os.path.abspath(__file__)),"Search results", dirname)
    output_filename = os.path.join(directory_name, filename)
    ensureDirectoryExists(directory_name)
    
    with open(output_filename, 'w') as f:
        f.write("### Search results for '_" + keyword + "_'<br />\n  ")
        f.write("__Number of projects__ : " + stats['nb_projects'] + "<br />\n")
        f.write("__Total aid sent in $__ :" + str(stats['total_contrib'])  + "<br />\n" )
        f.write("__Number of transactions ( *engagements included* )__ :" + str(stats['nb_transactions'])  + "<br />\n" )
        f.write("__Number of transactions ( *engagements excluded* )__ :" + str(stats['nb_transactions_sent'])  + "<br />\n")
        f.close()
        
    print("Stats written to file : " + output_filename)

def writeXMLProjectListToFile(project_list, dirname, filename):
    directory_name = os.path.join(os.path.dirname(os.path.abspath(__file__)),"Search results", dirname)
    output_filename = os.path.join(directory_name, filename)
    ensureDirectoryExists(directory_name)
    
    with open(output_filename, 'w') as f:
        f.write(getXMLString(project_list))
        
    print("Projects written to file : " + output_filename)

#################################################################
#                  MAIN SCRIPT SECTION
#################################################################

if __name__ == '__main__':
    all_projects = mergeXMLProjects([active_projects, closed_projects, terminating_projects])
    all_projects_no_duplicate = removeProjectDuplicates(all_projects)

    COUNTRY = ''
    KEYWORD = 'bangsamoro'

    all_found_projects = findProjectsByKeyWord(all_projects_no_duplicate, KEYWORD, False)
    stats = getProjectsStats(all_found_projects, COUNTRY)

    directory_name = KEYWORD
    writeStatsToFile(stats, directory_name, "README.md", KEYWORD)
    writeXMLProjectListToFile(all_found_projects, directory_name, "projects.xml")
