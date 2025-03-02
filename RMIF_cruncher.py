import csv
import os

#################################################################
#                   DATA PREPARATION SECTION
#################################################################
MRIF_PROJECTS_FILENAME = 'mrif_projects.csv'
mrif_projects_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'MRIF', MRIF_PROJECTS_FILENAME)

#################################################################
#                DATA ANALYSIS FUNCTIONS SECTION
#################################################################

''' NOTHING '''

#################################################################
#                   UTILITY FUNCTIONS SECTION
#################################################################

def getMRIFProjectsAsDictFromCSV(file_path):
    mrif_projects = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            mrif_projects.append(row)

    return mrif_projects

def getOrganismHashMapFromProjectsDict(project_list):
    org_list = {}
    
    for project in project_list:
        org_list[project['NoOrgaQue']] = {'NomOrgaQue':project['NomOrgaQue'], 'NomOrgaEtran':project['NomOrgaEtran']}

    return org_list

#################################################################
#                  CUSTOM CLASSES FOR DATA HANDLING
#################################################################
''' NOTHING '''

#################################################################
#                  MAIN SCRIPT SECTION
#################################################################

if __name__ == '__main__':
    mrif_data = getMRIFProjectsAsDictFromCSV(mrif_projects_file)
    print(len(mrif_data))

    sum_transactions = 0;
    for project in mrif_data:
        sum_transactions += (float(project['Versement1']) + float(project['Versement2']) + float(project['Versement3']) + float(project['Versement4']) + float(project['Versement5']))

    sum_engagements = 0
    for project in mrif_data:
        sum_engagements += float(project['MontantSubvention'])

    all_orgs = getOrganismHashMapFromProjectsDict(mrif_data)
                            
    print("Total international fund sent : " + str(sum_transactions))
    print("Total in engagements : " + str(sum_engagements))
    print("Number of organisations : " + str(len(all_orgs)))

    for org in all_orgs:
        print(all_orgs[org])
        
