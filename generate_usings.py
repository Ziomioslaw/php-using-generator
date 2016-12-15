import os, re

class ClassesDirectory():

    def __init__(self):
        self.classesDirectory = {}
        self.regex = re.compile('(class|interface) ([a-zA-Z0-9_]+)')

    def buildClassDirectory(self, phpDirectory):
        for root, dirs, files in os.walk(phpDirectory):
            for file in files:
                if not file.endswith('.php'):
                    continue

                path = os.path.join(root, file)
                self.getClassName(path)

    def getClassName(self, path):
        file = open(path, 'r')
        groups = re.findall(self.regex, file.read())
        if len(groups) == 0:
            return

        for group in groups:
            self.classesDirectory[group[1]] = path

    def analizeFile(self, filePath):
        file = open(filePath, 'r')
        fileContent = file.read()

        result = []

        result.extend(re.findall('new ([a-zA-Z_0-9]+)', fileContent))
        result.extend(re.findall('([a-zA-Z_0-9]+)::', fileContent))
        result.extend(re.findall('\([ \t]*([a-zA-Z_0-9]+)[ \t]*\$', fileContent))
        result.extend(re.findall('extends ([a-zA-Z_0-9]+)', fileContent))
        result.extend(re.findall('implements (.+) {', fileContent))

        return list(set(result))

    def generateUsings(self, filePath):
        usedClasses = self.analizeFile(filePath)
        normalizedFilePath = filePath.replace('\\', '/')
        results = []

        for usedClass in usedClasses:
            if not self.classesDirectory.has_key(usedClass):
                continue

            usedFilePath = self.classesDirectory[usedClass]
            commonPart = self.buildRelatedPath(normalizedFilePath, usedFilePath)
            if commonPart != '':
                commonPart = '/' + commonPart

            resultPath = "require_once(__DIR__ . '" + commonPart + '/' + os.path.basename(usedFilePath) + "');"

            results.append(resultPath.replace('\\', '/'))

        return results

    def buildRelatedPath(self, mainFile, usedFile):
        mainFileDirectory = os.path.dirname(mainFile)
        usedFileDirectory = os.path.dirname(usedFile)

        if mainFileDirectory == usedFileDirectory:
            return ''

        result = os.path.relpath(os.path.dirname(usedFile), os.path.dirname(mainFile))
        if result == '.':
            return ''

        return result

if __name__ == '__main__':
    import sys, getopt

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:f:", ["project=", "file="])
    except getopt.GetoptError as err:
        print('Usage: -p <project> -f <file>')

    project = None
    file = None

    for opt, arg in opts:
        if opt == '-h':
            print('Usage: -p <project> -f <file>')
            sys.exit()
        elif opt in ('-p', 'project'):
            project = arg
        elif opt in ('-f', 'file'):
            file = arg

    if project == None or file == None:
        print('Usage: -p <project> -f <file>')
        sys.exit()

    classDirectory = ClassesDirectory()
    classDirectory.buildClassDirectory(project)

    results = classDirectory.generateUsings(file)
    for result in results:
        print(result)
