import os


if __name__ == "__main__" :
  
  input_variable = os.environ['INPUT_STORE']
  print (f"Invar is {input_variable} ")

  isString = isinstance(input_variable, str)
  if isString:
    print ('Var is string')
  else:
    print ('Var is not a string')

  if input_variable: 
    print ('Acting as if it is true')
  else:
    print ('Acting as if it is false') 
