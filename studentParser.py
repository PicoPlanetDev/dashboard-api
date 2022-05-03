class StudentParser():
    def __init__(self, student):
        self.student = student

    def getCourses(self):
        sectionIds = [section['id'] for section in self.student['sections']]
        schoolCourseTitles = [section['schoolCourseTitle'] for section in self.student['sections']]
        return sectionIds, schoolCourseTitles

    def convertNameAndSection(self, input):
        def isId(a):
            try: int(a)
            except: return False
            print("ID")
            return True
            
        sectionIds, schoolCourseTitles = self.getCourses()
        
        if isId(input):
            convertDict = dict(zip(sectionIds, schoolCourseTitles))
            input = int(input)
        else: convertDict = dict(zip(schoolCourseTitles, sectionIds))
        return convertDict[input]

    def getTermNamesIds(self):
        termIds = [term['id'] for term in self.student['reportingTerms']]
        termNames = [term['title'] for term in self.student['reportingTerms']]
        return termIds, termNames

    def convertTermNameToIds(self, name):
        termIds, termNames = self.getTermNamesIds()
        termIdsForName = [termId for termId in termIds if termNames[termIds.index(termId)] == name]
        return termIdsForName

    def getGradesForTerm(self, termIdList):
        grades = []
        gradeSectionIds = []
        for termId in termIdList:
            for grade in self.student['finalGrades']:
                if grade['reportingTermId'] == termId:
                    grades.append([grade['grade'], grade['percent']])
                    gradeSectionIds.append(grade['sectionid'])
        return grades, gradeSectionIds

    def getGrade(self, sectionId, termIdList):
        grades, gradeSectionIds = self.getGradesForTerm(termIdList)
        return grades[gradeSectionIds.index(sectionId)]