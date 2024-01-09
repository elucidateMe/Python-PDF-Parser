import fitz # PyMuPDF reader
import re 
from os import listdir, path 

class pdfObject:
  # pdfButtonDict variable assumes there is only one button dictionary
  # pdfTableVarList assumes there is only one table list
  def __init__(self, pdfFile, pdfType = None):
    self.pdfFile = pdfFile
    self.pdfReturn = None
    if pdfType != None:
      self.pdfButtonDict = pdfType['button']
      self.pdfTableVarList = pdfType['table']
      self.pdfReturn = pdfType['return']
    self.dictOfNameValue()
 
  def __str__(self):
    return str(self.pdfDict)

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
  
  def checkPDFButton(self):
    for i in self.pdfDict[self.pdfButtonDict['buttonName']]:
      if i != 'Off':
        self.pdfDict[self.pdfButtonDict['buttonName']] = self.pdfButtonDict['button'][i]
        break

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
 
  def accessDict(self, item):
    return self.pdfDict[item]
 
  def specificReturn(self):
    if hasattr(self, 'pdfReturn'):
      tempList = []
      for item in self.pdfReturn:
        tempList.append(self.accessDict(item))
      return tempList

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

 
