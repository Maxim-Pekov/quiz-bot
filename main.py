from pprint import pprint
with open("quiz-questions/1vs1200.txt", "r", encoding="KOI8-R") as my_file:
    file_contents = my_file.read()
f = file_contents.split('\n\n')
slovar = {}
for key, i in enumerate(f):
    if 'Вопрос' in i:
        slovar[f[key]] = f[key + 1]
pprint(slovar)
