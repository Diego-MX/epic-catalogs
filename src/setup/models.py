


class ExcelReference: 
    def __init__(self, file, sheet, table): 
        self.file = file
        self.sheet = sheet
        self.table = table
    
    def load_table(self): 
        pass


class ExcelDataFrame: 
    def __init__(self, reference:ExcelReference, )