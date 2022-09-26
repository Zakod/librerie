
def GN(determinant, nom, n, genre = 'm', lettre_pluriel = 's', adjectif = "", maj = 'M'):
	k = 0
	articles = {'indéfini' : ('un ', 'une ', 'des '), 'défini' : ('le ', 'la ', 'les ', "l'"), 'numéral' : (str(n),)}
	if genre == 'f' :
		k +=1
	if nom[0] in ('a','e','é','è','ê', 'ë', 'i', 'î','ï', 'o', 'ô', 'ö', 'u', 'û', 'ü', 'ù', 'y') :
		if n == 1 :
			k = 3
	if n > 1 :
		k = 2
		nom += lettre_pluriel
		if adjectif != "" :
			adjectif += lettre_pluriel
	if determinant == 'numéral' :
		k = 0
	return articles[determinant][k] + " " + nom + " " + adjectif + " "

def nom(mot, n, lettre_pluriel = 's'):
	if n > 1 :
		pluriel = lettre_pluriel
	else :
		pluriel = ""
	return mot + pluriel

def article(genre):
	if genre == 'm' :
		return " un "
	else :
		return " une "