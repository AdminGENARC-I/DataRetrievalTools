import xlsxwriter
import json
import pandas as pd

class Project:
    def __init__(self, id):
        self.id = id
        self.location = ''
        self.year = ''
        self.image_urls = []
        self.topics = []

if __name__ == '__main__':
    projects = {}
    
    with open('./topics_og.json', 'r') as topics:
        inputData = pd.read_excel('./inputData.xlsx')
        for index, row in inputData.iterrows():
            id, url, location, year = str(row[1]), row[10], row[4], row[2]

            if projects.get(id) == None:
                projects[id] = Project(id)
            
            if not url in projects[id].image_urls:
                projects[id].image_urls.append(url)
            
            if projects[id].location == '':
                projects[id].location = location
            
            if projects[id].year == '':
                projects[id].year = year
        
        topicsData = json.load(topics)
        for project_id in topicsData["projects"].keys():
            if projects.get(project_id) != None:
                for topic in topicsData["projects"][project_id]:
                    projects[project_id].topics.append(topic)

        workbook = xlsxwriter.Workbook('./outputData.xlsx')
        worksheet = workbook.add_worksheet()
        row_index = 0
        for project in projects.values():
            worksheet.write_string('A{0}'.format(row_index), str(project.id))
            worksheet.write_string('B{0}'.format(row_index), str(project.location))
            worksheet.write_string('C{0}'.format(row_index), str(project.year))
            worksheet.write_string('D{0}'.format(row_index), ', '.join(list(map(lambda topic: str(topic), project.topics))))
            worksheet.write_string('E{0}'.format(row_index), ', '.join(list(map(lambda url: str(url), project.image_urls))))
            row_index += 1
        
        workbook.close()