from random import randrange
import re
from datetime import datetime

def codeCaractere(chaine):
    liste_codes = []
    for c in chaine :
        liste_codes.append(ord(c))
    return liste_codes

def faireListe(victimes) :#[2, 5, [7-10]]
    victimes += ','
    victimes = victimes.replace(' ', '')
    print(victimes)
    nb_plages = victimes.count(',')
    identifiants = []
    for p in range(nb_plages) :
        virgule = victimes.find(',')
        plage = victimes[:virgule]#une valeur, ou une plage de valeurs consécutives
        crochet_ouvrant = plage.find('[')
        if crochet_ouvrant > -1 :
            tiret = plage.find('-')
            crochet_fermant = plage.find(']')
            debut_plage = int(plage[1:tiret])
            fin_plage = int(plage[tiret+1:crochet_fermant])
            for i in range(fin_plage - debut_plage + 1) :
                identifiants.append(debut_plage + i)
        else :
            identifiants.append(int(plage))
        victimes = victimes[virgule+1:]
    return identifiants#liste d'entiers

def estDateTemps(chaine, temps = 'minute') :
    if temps == 'date' :
        reg = '[0-9]{4}-[0-9]{2}-[0-9]{2}'
    elif temps == 'heure' :
        reg = '[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}'
    elif temps == 'minute' :
        reg = '[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}'
    #reg = '[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}'
    x = re.search(reg, chaine)
    if x :
        return x.group()
    else : return None

def tabul(n, saut_de_ligne = True) :
    indentation = ""
    if saut_de_ligne :
        indentation = "\n"
    for i in range(n) :
        indentation += '    '
    return indentation

def chaine(liste) :
    chaine = ""
    for bout in liste :
        chaine += bout + ", "
    chaine = chaine[:len(chaine) - 2]
    print("chaine = ", chaine)
    return chaine

def sortirPremierMot(chaine) :
    espace = chaine.find(' ')
    return chaine[:espace]

def dateHeureFrancaise(date_heure, mode = 'ammjh') :
    mois_francais = {'01' : 'janvier',
            '02' : 'février',
            '03' : 'mars', 
            '04' : 'avril', 
            '05' : 'mai', 
            '06' : 'juin', 
            '07' : 'juillet', 
            '08' : 'août', 
            '09' : 'septembre', 
            '10' : 'octobre', 
            '11' : 'novembre',
            '12' : 'décembre'}

    annee = date_heure[:4]
    mois = mois_francais[date_heure[5:7]]
    jour = str(int(date_heure[8:10]))
    heure = str(int(date_heure[11:13]))
    minute = str(int(date_heure[14:16]))
    if mode == 'auto' :
        maintenant = str(datetime.now())
        annee_maintenant = maintenant[:4]
        print("now = ", annee_maintenant, "année = ", annee)
        if annee == annee_maintenant :
            mode = 'mj'
        else : mode = 'amj'
    if mode == 'mj' : date = jour + " " + mois
    elif mode == 'amj' : date = jour + " " + mois + " " + annee
    elif mode == 'ammjh' : date = jour + " " + mois + " " + annee + " " + heure + " h " + minute
    return date

def urliser(mot) :
    sales_caracteres = {    'éèêëÉÈÊË'  : 'e',
                            'àâäÀÂÄ'    : 'a',
                            'îïÎÏ'      : 'i',
                            'ôöÔÖ'      : 'o',
                            'ùûüÙÛÜ'    : 'u',
                            'çÇ'        : 'c',
                            ' '         : '_',
                            '"'         : '',
                            "'"         : '',
                            "?!,.;:/%"  : '-'
                            }
    mot_sans_accent = ''
    for i in mot :
        for j in sales_caracteres :
            if i in j :
                i = sales_caracteres[j] ; break
        mot_sans_accent += i.lower()
    return mot_sans_accent

def motDePasseValide(mot, signes) :
    if len(mot) < 8  or len(mot) > 12 : return False
    minuscules = "abcdefghijklmnopqrstuvwxyzéèêëâäàîïôöùûüç"
    majuscules = minuscules.upper()
    chiffres ="0123456789"
    le_tout = minuscules + majuscules + chiffres + signes
    minus, majus, chif, signe = False, False, False, False
    for c in mot :
        if c not in le_tout : return False
        if c in minuscules : minus = True
        if c in majuscules : majus  = True
        if c in chiffres : chif = True
        if c in signes : signe = True
    return minus and majus and chif and signe

def unMois() :
    return 2678400

def urlAlea() :
    lettres = "abcdefghijklmnopqrstuvwxyz"
    url = ""
    for i in range(12) :
        url += lettres[randrange(26)]
    return url

def pseudoDispo(pseudo) :#on sort avec True si le pseudo est disponible
    
    def testerToutesCasses(p, pseudo) :#si on rencontre un caractères qui n'est pas pareil, on sort avec True
        pareil = True
        for i in range(len(p)) :
            pareil = (pseudo[i] in [p[i].upper(), p[i].lower()])
            if pareil == False:
                break
        return not pareil
    
    try :
        p = open('pseudos.txt', 'r') 
    except :
        p = open('pseudos.txt', 'a')
    p.close()
    p = open('pseudos.txt', 'r') 
    pseudos = p.readlines()
    p.close()
    disponible = True
    for p in pseudos :
        p = p[:len(p)-1]
        print("p = ", p)
        if len(p) == len(pseudo) :
            disponible = testerToutesCasses(p, pseudo)
        else :
            disponible = True
    return disponible
 
def pseudoValide(pseudo) :
    minuscule = "abcdefghijklmnopqrstuvwxyzéèêëâäàîïôöùûüç"
    majuscule=minuscule.upper()
    domaine_libre = minuscule + majuscule + ' -'
    valid = True
    for c in pseudo :
        print(c)
        if c in domaine_libre :
            pass
        else :
            valid = False
            break
        print(valid)
    return valid

def lettreChiffre(mot, litterature = False) :
    minuscule = "abcdefghijklmnopqrstuvwxyzéèêëâäàîïôöùûüçœ"
    majuscule=minuscule.upper()
    #print(majuscule) 
    chiffre ="0123456789"
    if litterature :
        signes = "'’°.,?!:€$;-(—)«» %*\n\r\t" + '"' + chr(8232)#»«
    else :
        signes = "- "
    domaine_libre = minuscule + majuscule + chiffre + signes
    valid = True
    for c in mot :
        print(c)
        if c in domaine_libre :
            pass
        else :
            valid = False
            print("refusé : ", c)
            break
        print(valid)
    return valid

def mailValide(mail) :
    arobase = mail.find('@')
    if arobase == -1 :
        return False
    else :
        avant = mail[:arobase]
        apres = mail[arobase + 1 :]
        minuscule = "abcdefghijklmnopqrstuvwxyzéèêëâäàîïôöùûüç"
        majuscule=minuscule.upper()
        chiffre ="0123456789"
        #signes = ""
        le_tout = minuscule + majuscule + chiffre + signes_mot_de_passe
        valid = True
        for c in avant :
            if c in le_tout :
                pass
            else :
                valid = False
                break
        if valid :
            for c in apres :
                if c in le_tout :
                    pass
                else :
                    valid = False
                    break
        return valid

def mmotDePasseAlea(signes):
    dico_mp = {}
    minuscules = "abcdefghijklmnopqrstuvwxyzéèêëâäàîïôöùûüç"
    majuscules = minuscules.upper()
    chiffres ="0123456789"
    le_tout = minuscules + majuscules + chiffres + signes
    longueur = 8 + randrange(5)
    for i in range(longueur):
        dico_mp[i] = None   
    minus = minuscules[randrange(len(minuscules))]
    majus = majuscules[randrange(len(majuscules))]
    chiffre = chiffres[randrange(len(chiffres))]
    signe = signes[randrange(len(signes))]
    place_minuscule, place_majuscule = randrange(longueur), randrange(longueur - 1)
    place_signe, place_chiffre = randrange(longueur - 2), randrange(longueur - 3)
    print("p.minus = ", place_minuscule, "p.majus = ", place_majuscule, "p.signe = ", place_signe, "p.chif = ", place_chiffre)
    
    dico_mp[place_minuscule] = minus
    if place_majuscule >= place_minuscule :
        place_majuscule = place_majuscule + 1
    print("p.minus = ", place_minuscule, "p.majus = ", place_majuscule, "p.signe = ", place_signe, "p.chif = ", place_chiffre)    
    
    dico_mp[place_majuscule] = majus
    mini, maxi = min(place_minuscule, place_majuscule), max(place_minuscule, place_majuscule)
    print("mini = ", mini, "maxi = ", maxi)
    
    if place_signe >= maxi : place_signe = place_signe + 1
    elif place_signe >= mini : place_signe = place_signe + 1
    print("p.minus = ", place_minuscule, "p.majus = ", place_majuscule, "p.signe = ", place_signe, "p.chif = ", place_chiffre)
    dico_mp[place_signe] = signe
    minimini, maximaxi = min(place_signe, mini), max(place_signe, maxi)
    #ps, mini, maxi
    #mini, ps, maxi
    #mini, maxi, ps
    if minimini == place_signe : milieu = mini
    elif maximaxi == place_signe : milieu = maxi
    else : milieu = place_signe
    print("minimini = ", minimini, "milieu = ", milieu, "maximaxi = ", maximaxi)
    if place_chiffre >= maximaxi : place_chiffre = place_chiffre + 3
    elif place_chiffre >= milieu : place_chiffre = place_chiffre + 2
    elif place_chiffre >= minimini : place_chiffre = place_chiffre + 1
    print("p.minus = ", place_minuscule, "p.majus = ", place_majuscule, "p.signe = ", place_signe, "p.chif = ", place_chiffre)
    dico_mp[place_chiffre] = chiffre
    print("dico_mp = ", dico_mp) 
    #for c in dico_mp :
    chaine = ""
    for i in range(longueur) :
        if i not in [place_minuscule, place_majuscule, place_signe, place_chiffre] :
            dico_mp[i] = le_tout[randrange(len(le_tout))]
        chaine += dico_mp[i]
    print("dico_mp = ", dico_mp)
    return chaine

def motDePasseAlea(signes):
    dico_mp = {}
    minuscules = "abcdefghijklmnopqrstuvwxyzéèêëâäàîïôöùûüç"
    majuscules = minuscules.upper()
    chiffres ="0123456789"
    le_tout = minuscules + majuscules + chiffres + signes
    longueur = 8 + randrange(5)
    for i in range(longueur):
        dico_mp[i] = None
    places_disponibles = []
    for p in range(longueur) :
        places_disponibles.append(p)

    minuscule = minuscules[randrange(len(minuscules))]
    majuscule = majuscules[randrange(len(majuscules))]
    chiffre = chiffres[randrange(len(chiffres))]
    signe = signes[randrange(len(signes))]

    place_minuscule = randrange(longueur) 
    dico_mp[place_minuscule] = minuscule
    places_disponibles.remove(place_minuscule)

    place_majuscule = randrange(longueur - 1)
    place_majuscule = places_disponibles[place_majuscule]
    dico_mp[place_majuscule] = majuscule
    places_disponibles.remove(place_majuscule)

    place_chiffre = randrange(longueur - 2)
    place_chiffre = places_disponibles[place_chiffre]
    dico_mp[place_chiffre] = chiffre
    places_disponibles.remove(place_chiffre)

    place_signe = randrange(longueur - 3)
    place_signe = places_disponibles[place_signe]
    dico_mp[place_signe] = signe
    
    print("p.minus = ", place_minuscule, "p.majus = ", place_majuscule, "p.chif = ", place_chiffre, "p.signe = ", place_signe)
    print("dico_mp = ", dico_mp) 
    chaine = ""
    for i in range(longueur) :
        if i not in [place_minuscule, place_majuscule, place_signe, place_chiffre] :
            dico_mp[i] = le_tout[randrange(len(le_tout))]
        chaine += dico_mp[i]
    print("dico_mp = ", dico_mp)
    return chaine



