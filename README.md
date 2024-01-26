# Python PDF Parser
This Pdf Parser creates a python object which consists of the values of inputted fields within a PDF using PyMUPdf, which by default will print as a json

## Initilization

The initialization requires the file location of the pdf
The pdfType option is for formatting purposes as certain fields are retrieved by default are not human readable
```
  def __init__(self, pdfFile, pdfType = None):
    self.pdfFile = pdfFile
    self.pdfReturn = None
    if pdfType != None:
      self.pdfButtonDict = pdfType['button']
      self.pdfTableVarList = pdfType['table']
      self.pdfReturn = pdfType['return']
    self.dictOfNameValue()
```

dictOfNameValue creates a json-esque object and stores it within self.pdfDict
```
  def dictOfNameValue(self) -> dict:
    container = {}
    with fitz.open(self.pdfFile) as pdf:
      thing = pdf[0].widgets()
      for i in thing:
        if container.get(i.field_name) != None:
          if type(container[i.field_name]) != list: #check to see if a field has multiple values (currently only seen in buttons)
            container[i.field_name] = [container[i.field_name]]
            container[i.field_name].append(i.field_value)
          else:
            container[i.field_name].append(i.field_value)
        else:
          container[i.field_name] = i.field_value
    self.pdfDict = container
    if hasattr(self, 'pdfButtonDict'):
      self.checkPDFButton()
    if hasattr(self, 'pdfTableVarList'):
      self.tableSortPdf()
```

## pdfType Formatting
This is a dictionary contained outside the pdfObject class which helps interpret certain input field types within the PDF
In order to create this dictionary, you must know how the inputs are stored on the PDF itself, which can be done by printing an initial parse of a PDF
```
pdfType = {
  'example' : {
    #button consists of a dict of what order button represents what visually on the pdf and how the button is named internally on the pdf
    'button' : {
      'button' : {'0' : 'Bad',
                  '1' : 'Ok',
                  '2' : 'Good',
                  },
      'buttonName' : 'Group1'
                },
    #the internal names of the 'rows' (visually columns) in a table in the pdf
    'table' : ['DAYRow1', 'MONTHRow1', 'YEARRow1', 'HOURS bRow1',
                'POINTS cRow1', 'LOCATION dRow1'],
    #what data is generically desired from the pdf, it is a list of the desired item(s) as they are named internally
    'return' : ['1 DATE', '5 NAME', 'POINTS cRow1']
    }
}
```
### Button
Buttons in a group will be interpreted as a generic list, Where a button being "on" is indicated by a change from 'Off' into '\<index position>'. i.e.
```
'Group1': ['0', 'Off', 'Off']
```

The button formatting option currently prints the button the first button that is recognized as "on" in accordance 
```
  def checkPDFButton(self):
    for i in self.pdfDict[self.pdfButtonDict['buttonName']]:
      if i != 'Off':
        self.pdfDict[self.pdfButtonDict['buttonName']] = self.pdfButtonDict['button'][i]
        break
```

The above example would now be:
```
'Group1': 'Bad'
```

### Table
Table columns will be stored as a string with many return lines. i.e.
```
'DAYRow1': '25\r\r26 \r\r\r'
```

The table formatting option currently creates a list by splitting by whatever separating character there is.
By default, the separator is any amount of return characters.
```
  def tableSortPdf(self, sep = r'\r+'):
    #rows in pdfTableVarList are visually the columns of the table, variables are called rows just for consistency
    self.pdfDict['table'] = {}
    tempList = []
    for row in self.pdfTableVarList:
      exec(f'self.pdfDict["{row}"] = re.split(r"{sep}", self.pdfDict["{row}"])') # stored in local variable to remove excess information from pdfDict
      exec(f'tempList.append(self.pdfDict["{row}"])')
    for i in range(len(tempList[0])):
      self.pdfDict['table'][f'statement {i}'] = []
      for row in tempList:
        self.pdfDict['table'][f'statement {i}'].append(row[i])
```

The above example would now be:
```
'DayRow1' = ['25','26','']
```
