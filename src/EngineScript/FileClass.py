class File:
    def __init__(self, name, fullName, size, extension, modified, hash):
        self.__name = name
        self.__fullName = fullName
        self.__size = size
        self.__extension = extension
        self.__modified = modified
        self.__hash = hash

        self.__fileData = {
            "name" : self.__name,
            "fullName" : self.__fullName,
            "size" : self.__size,
            "extension" : self.__extension,
            "modified" : self.__modified
        }


    ''' getters '''
    def getName(self):
        return self.__name


    def getFullName(self):
        return self.__fullName


    def getSize(self):
        return self.__size


    def getExtension(self):
        return self.__extension


    def getModified(self):
        return self.__modified


    def getDataFile(self):
        return self.__fileData


    def getHash(self):
        return self.__hash


    ''' Вспомогательные функции '''
    def display(self):
        print(self.__name)

