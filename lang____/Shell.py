import lang__ as lg

while True:
    text = input('basic > ')
    result, error = lg.run('<stdin>' , text)
    if error:
        print(error.as_string())
    else:
        print(result)