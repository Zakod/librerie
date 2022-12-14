#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from bottle import run, route, view, static_file, template, request, error, response, FormsDict
from time import sleep
from outils import *
import sqlite3
from grammaire import GN, nom
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from os import remove, path, environ, getenv
from hashlib import sha512
#from dotenv import load_dotenv

def htmlMail(texte) :
    html = '<html>\n<body>\n<p>'
    for c in texte :
        if c == '\n' : html += '<br/>'
        else : html += c
    html += '<a href="www.vaste-programme/">vaste-programme.fr</a></p></body></html>'
    return html

def ecrireMail(msg, mail, objet) :
    #load_dotenv()
    smtp_adresse = 'mail56.lwspanel.com'
    smtp_port = 465
    email_adresse = 'contact@vaste-programme.fr'
    email_MP = getenv('MOT_DE_PASSE_MAIL')
    message = MIMEMultipart("alternative")
    message["Subject"] = objet
    message["From"] = email_adresse
    message["To"] = mail   
    html = htmlMail(msg)   
    texte_mime = MIMEText(msg, 'plain')
    html_mime = MIMEText(html, 'html')
    message.attach(texte_mime)
    message.attach(html_mime)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    with smtplib.SMTP_SSL(smtp_adresse, smtp_port, context=context) as server:
        server.login(email_adresse, email_MP)
        server.ehlo()
        server.sendmail(email_adresse, mail, message.as_string())

def voirMiniatures(radicande):
    url = "html/" + radicande + ".html"
    try :
        f = open(url, 'r')
        ligne_miniatures = f.readline()
        f.close()
    except :
        ligne_miniatures = "Impossible d'ouvrir le fichier html."
        journalErreurs("voirMiniatures : impossible d'ouvrir le fichier html.") 
    photos = []
    nb_photos = ligne_miniatures.count('§')
    for i in range(nb_photos) :
        src = ligne_miniatures.find('src=')
        ligne_miniatures = ligne_miniatures[src + 4:].strip()#
        larg = ligne_miniatures.find('width=')
        chemin_nom = ligne_miniatures[:larg].strip()
        ligne_miniatures = ligne_miniatures[larg+6:].strip()#
        haut = ligne_miniatures.find('height=')
        largeur = ligne_miniatures[: haut].strip()
        ligne_miniatures = ligne_miniatures[haut+7:].strip()#
        alt = ligne_miniatures.find('alt=')
        hauteur = ligne_miniatures[: alt].strip()
        ligne_miniatures = ligne_miniatures[alt+4:].strip()#
        paragraf = ligne_miniatures.find('§')
        alternate = ligne_miniatures[: paragraf].strip()
        html = "<img src=" + chemin_nom + " width=" + largeur + " height=" + hauteur + " alt=" + alternate + "/>"
        photos.append(html)
    return photos

def cestQui() :
    #qui = request.get_cookie("connecte")
    qui = None
    if qui :
        url = "espace_personnel"
    else :
        url = "connexion"        
        qui = "connexion"
    lien = '<a href = ' + url + '>' + qui + '</a>'
    return  lien

def cleDeValeur(dico, valeur, indice) :#(titres_de_blogs[b], 'blog' + str(b), approbations[b]) 
    for k, info in dico.items() :
        if info[indice] == valeur :
            return k
    return None

def incrementCompteur(table, colonne, identifiant, nombre = 1) :
    branche = sqlite3.connect('vasteprogramme.db')
    curseur = branche.cursor()
    donnees = (colonne, table, identifiant)
    req = "SELECT " + colonne + " FROM " + table + " WHERE id = ?"
    curseur.execute(req, (identifiant,))
    compteur = curseur.fetchone()
    if compteur != None :
        compte = compteur[0]
        compte += nombre
        req = "UPDATE " + table + " SET " + colonne + " = ? WHERE id = ?"
        donnees = (compte, identifiant)
        curseur.execute(req, donnees)
        branche.commit()
    else :
        journalErreurs("incrementCompteur ; rien dans " + table + " qui ait comme id. " + str(identifiant) + " ; ou pas de colonne " + colonne + " dans " + table)
    curseur.close()
    branche.close()
    
@error(404)
def error404(error):
    return "<h1>Cette page n'est pas encore écrite. Prenez patience, ça ne saurait tarder...</h1>"

def initialisationBd() :
    for t in definitions_table :
        initialisationTable(t)

def initialisationTable(table) :
    branche = sqlite3.connect('vasteprogramme.db')
    curseur = branche.cursor()
    req = "CREATE TABLE " + table + " (" + definitions_table[table] + ")"
    curseur.execute(req)
    branche.commit()
    curseur.close()
    branche.close()

@route("/rase_table", method = 'POST')
@view("rase_table.tpl")
def raseTable() :
    message, titre, retour = "", "Réinitialisation de la table ", "</br></br></br>\n<a href = 'sesam'>page du patron</a>"
    if request.forms.envoi_drop :
        nom_table = request.forms.table
        if nom_table != '':
            #attention = '<p class = "alerte"> Je suis sûr ? Ça efface toute une table !</p>'
            #annuler = '<a href = "sesam">Annuler</a>'
            branche = sqlite3.connect('vasteprogramme.db')
            curseur = branche.cursor()
            kapout = "DROP TABLE " + nom_table
            try :
                curseur.execute(kapout)
                curseur.commit()
            except :
                pass
            curseur.close()
            branche.close()
            initialisationTable(nom_table)
            message = "La table " + nom_table + " a été réinitialisée."
    return {"titre" : titre + nom_table, "message" : message + retour}

def miseAJour(table, colonne, valeur, critere_identifiant, valeur_identifiante) :
    branche = sqlite3.connect('vasteprogramme.db')
    curseur = branche.cursor()
    req = "UPDATE " + table + " SET " + colonne + " = ? WHERE " + critere_identifiant + " = ?"
    curseur.execute(req, (valeur, valeur_identifiante))
    branche.commit()
    curseur.close()
    branche.close()
    return "la colonne " + colonne + " de la table " + table + " a pour nouvelle valeur : " + valeur

def afficherSelection(chose, table_ou_nom, tail_champs) :#selection ou table entière
    base = 3
    section = tabul(base) + "<table>"
    section += tabul(base + 1) + "<caption>" + table_ou_nom + "</caption>"
    for a in chose :
        ligne = tabul(base + 1) + "<tr>"
        i = 0
        for champ in a :
            champ = str(champ)
            x = estDateTemps(champ)
            if x :
                champ = dateHeureFrancaise(x)
            ligne += tabul(base + 2) + "<td class = '" + tail_champs[i] + "'>" + champ + "</td>"
            i += 1
        ligne += tabul(base) + "</tr>\n"
        section += ligne
    section += tabul(base) + "</table>\n"
    return section

def requeteTable(nom, requete, donnees, requete_donnees, action_dans_table, tail_champs) : #SELECT (afficher résultat) , UPDATE, DELETE (afficher lignes éditées ?)
    table = urliser(nom)
    branche = sqlite3.connect('vasteprogramme.db')
    curseur = branche.cursor()
    if action_dans_table != 'suppression' :
        action = sortirPremierMot(requete)
        try :
            if donnees :
                curseur.execute(requete, donnees)
            else :#SELECT *
                curseur.execute(requete)
            if action == "SELECT" :
                chose = curseur.fetchall()
                if chose != [] :
                    section = afficherSelection(chose, nom, tail_champs)
                else :
                    journalErreurs("requeteTable ; la requête " + requete + " a rendu une liste vide.")
                    section = ""
            elif action == "UPDATE" :
                branche.commit()
                section = "La ligne a été modifiée."                    
        except :
            section = "<p class = alerte>Problème. La requête " + action + " dans " + nom + " n'a pu avoir lieu</p>"
    else :
        try :
            for req_don in requete_donnees :
                curseur.execute(req_don[0], req_don[1])          
            branche.commit()
            section = GN('numéral', "ligne", len(requete_donnees), genre = 'f', adjectif =  'supprimée')                    
        except :
            section = "<p class = alerte>Problème. La requête " + action + " dans " + nom + " n'a pu avoir lieu</p>"
    curseur.close()
    branche.close()    
    return section

def formulaireDrop(nom) :
    base  = 3
    table = urliser(nom)
    debut = tabul(base) + '<form class = "alerte" method="post" action="rase_table">' + tabul(base) + '<p>(RÉ)INITIALISER LA TABLE'
    milieu = tabul(base + 1) + '<label for="' + table + '">' + nom.upper() + '</label>'
    fin = tabul(base + 1) + '<input type="checkbox" name="table" value =' + table + ' id="table"/>'
    unput = tabul(base + 1) + '<input type="submit" name="envoi_drop" value="RÉINITIALISER" />' + tabul(base) + '</p>' + tabul(base) + '</form>'   
    return debut + milieu + fin + unput

def choisirCritere(base, egal = False) :   
    if egal :
        select = tabul(base + 1) + "<label for = 'valeur'>valeur  = </label>"
        select += tabul(base + 1) + '<input autocorrect = "off" type = "text" name = "valeur" id = "valeur" required/>'
        select += tabul(base + 1) + "<label for = 'identifiant'>id = </label>"
        select += tabul(base + 1) + '<input type = "text" name = "identifiant" id = "identifiant" size = "5" required/>'
    else :
        criteres  = ['=', '!=', '<', '<=','>','>=']
        select = tabul(base) + '<select name = "critere" id = "critere">'
        for c in criteres :
            if c == '=' :
                requis = 'selected'
            else :
                requis = ''
            select += tabul(base + 1) + '<option value="' + c + '" ' + requis + '>' + c + '</option>'
        select += tabul(base) + '<input type = "text" name = "valeur" id = "valeur" required/>'
        select += tabul(base) + '</select>'
    return select

def formulaireRechercheEditionSuppression(nom, cas, champs) :
    base = 3
    table = urliser(nom)
    choisir_colonne = ""    
    choisir_victime = ""
    debut = tabul(base) + '<form class = "horiz" method="post" action="sesam">'
    if cas == 'recherche' :
        titre = "Recherche dans la table "
        envoi = "envoi_recherche"
        choisir_critere = choisirCritere(base + 1) 
        suppression = False      
    elif cas == 'edition' :
        titre = "Modifier une ligne de la table "
        envoi = "envoi_edition"
        choisir_critere = choisirCritere(base + 1, egal = True)
        suppression = False 
    else :
        titre = "Supprimer une ligne de la table "
        envoi = "envoi_suppression"
        choisir_critere = ""
        suppression = True
    if suppression :
        choisir_victime += tabul(base + 1) + "<label for = 'victime'>" + titre + nom + '</label><br />'
        choisir_victime += tabul(base + 1) + "<input name = 'victime' id = 'victime' type = 'texte' size = '10' required/>"
    else :
        choisir_colonne += tabul(base + 1) + '<label for="champs">' + titre + nom + '</label><br />'
        choisir_colonne += tabul(base + 1) + '<select name="champs" id="champs">'
        for champ in champs[table] :
            champ = sortirPremierMot(champ)
            choisir_colonne += tabul(base + 2) + '<option value="' + champ + '"><p>' + champ + '</p>' + tabul(base + 2) + '</option>'
        choisir_colonne += tabul(base + 1) + '</select>'
    bouton_envoi = tabul(base + 1) + '<input type = "hidden" name = "nom_table" id = "nom_table" value = "' + nom + '"/>'
    bouton_envoi += tabul(base + 1) + '<input type = "submit" name = "' + envoi + '" value = "envoi"/>'
    fin = tabul(base) + '</form>'
    return debut + choisir_colonne + choisir_critere + choisir_victime + bouton_envoi + fin

def gestionTable(nom, requete, donnees, requete_donnees, action_dans_table) :
    table = urliser(nom)
    base = 3
    lignes_affichees = "<div class = 'g_t' id = '" + table + "'>"
    lignes_affichees += requeteTable(nom, requete, donnees, requete_donnees, action_dans_table, tailles_champs[table])
    formulaire_recherche = formulaireRechercheEditionSuppression(nom, 'recherche', champs_table) + tabul(base)
    formulaire_edition = formulaireRechercheEditionSuppression(nom, 'edition', champs_table_modifiables) + tabul(base)
    formulaire_suppression = formulaireRechercheEditionSuppression(nom, 'suppression', champs_table) + tabul(base)
    bouton_drop = formulaireDrop(nom) + tabul(base) + "</div>"
    return lignes_affichees + formulaire_recherche + formulaire_edition + formulaire_suppression + bouton_drop

def listeApprobation(patron = False, num_blog = -1, base = 3) :# class = 'liste_horizontale
    if patron :
        bl = blogs.copy()
    else :
        bl = blogs_quidam.copy()

    corps = tabul(base) + "<h3>choisir le blog :</h3>" #<p>
    for b, info in bl.items() :
        if num_blog > -1 and info[2] == approbations[num_blog]:
            coche = "checked"
        else : 
            coche = ""
        corps += tabul(base) + '<input type="radio" name="approbation" value="' + info[2] + '" id="' + info[2] + '" ' + coche +  '/>'
        corps += tabul(base) + '<label for="' + info[2] + '"> ' + b + '</label><br/>\n'    
    return corps

def listeMiniatures(photos, base = 3) :
    n = len(photos)
    corps = tabul(base) + "<h2>photo en sommaire :</h2>"
    corps += tabul(base) + "<div class = 'miniatures'>"
    for i in range(n) :
        numero_image = str(i + 1)
        corps += tabul(base + 1) + '<div class = "miniature">'
        corps += tabul(base + 2) + '<div class = "ligne_titre_miniature">'
        corps += tabul(base + 3) + '<label for="miniature">numéro ' + numero_image + '</label>'
        corps += tabul(base + 3) + '<input type="radio" name="miniature" value="' + numero_image + '" id="' + numero_image + '" required/>'
        corps += tabul(base + 2) + '</div>'
        corps += tabul(base + 2) + '<p>' + photos[i] + '</p>'
        corps += tabul(base + 1) + '</div>'
    return corps + tabul(base) + '</div>'

def formulaire(action, envoi, colonnes, titre = "", une_ligne = False, renseigne = False, base = 3, creation = False) :
    valeur = "envoi"    
    if une_ligne :
        brek = ""
    else :
        brek = '</br>'
          
    formulaire = tabul(base) +'<form action="' + action + '" method="POST">'   
    formulaire += tabul(base + 1) + "<h3>" + titre + "</h3>"      
    for champ in colonnes :
        formulaire += tabul(base + 1) +'<div class = "champ">'
        nom = urliser(champ[0])
        bulle = ""
        if nom == "mot_de_passe" :
            typ_input = "password"
            if creation :
                bulle = 'title = "' + title_mot_de_passe + '" '
            else : bulle = ""
        else :
            typ_input = "text"
        if nom == "pseudo" :
            if creation :
                bulle = 'title = "'  + title_pseudo + '" '
            else : bulle = ""
        if renseigne and champ[0] != 'mot de passe':
            valu = 'value = "' + champ[2] + '" '
        else :
            valu = ''
        ligne = tabul(base + 2) +'<label for="' + nom + '">' + champ[0] + '</label>'
        ligne += brek + tabul(base + 2) +'<input autocorrect = "off" type="' + typ_input + '" ' + bulle + ' name="' + nom + '" id="' + nom
        ligne += '" size="' + champ[1] + '" maxlength="' + champ[1] + '" ' + valu + 'required /><br/>' + brek
        formulaire += ligne
    formulaire += tabul(base + 2) +'<input type="submit" name="' + envoi + '" value="' + valeur + '"/></div>'
    formulaire += tabul(base + 1) + '</div>'
    formulaire += tabul(base) + '</form>'   
    return formulaire

def publication(action, envoi, auteur = "", titre = "", num_blog = -1, base  = 3, id_article = -1) :
    value_chapeau = ""
    value_consignes = ""
    value_texte = ""
    if id_article > -1 :#modification
        branche = sqlite3.connect('vasteprogramme.db')
        curseur = branche.cursor()
        req = "SELECT titre, auteur, chapeau, texte, consignes, approbation FROM articles WHERE id = ?"
        curseur.execute(req, (id_article,))
        article = curseur.fetchone()
        curseur.close()
        branche.close()
        if article != None :
            titre = article[0]
            auteur = article[1]
            value_chapeau = article[2]
            value_texte = article[3]
            value_consignes = article[4]
            num_blog = approbations.index(article[5])
        else :
            journalErreurs("publication ; rien dans articles qui ait comme id. " + str(id_article))
        input_id_article = tabul(base + 1) + '<input type = "hidden" name = "id_article" id = "id_article" value = "' + str(id_article) + '"/>'
    else : input_id_article = ""
  
    formulaire = tabul(base, True) + '<form action="' + action + '" method="POST">' + input_id_article
    if auteur == 'Jean-Max' :
        #requis = ""
        ridonli = 'readonly'
        lm = listeMiniatures(voirMiniatures(urliser(titre)), base = base + 1)
        formulaire += listeApprobation(patron = True, num_blog = num_blog, base = base + 1) + lm
        le_texte = ""
        les_consignes = ""
    else :
        ridonli = ''
        if num_blog > -1 :
            formulaire += listeApprobation(patron = False, num_blog = num_blog)
        else :
            formulaire += listeApprobation(patron = False)
        le_texte = tabul(base + 1) + "<label for='texte'>texte de l'article</label><br/>"
        le_texte += tabul(base + 1) + '<textarea title = "' + title_litterature + '" name="texte" id="texte"  cols="80" rows="20" required/>' + value_texte + '</textarea><br/>'
        les_consignes = tabul(base + 1) + '<label for="consignes">consignes de mise en forme</label><br/>'
        les_consignes += tabul(base + 1) + '<textarea title = "' + title_300 + '" name="consignes" id="consignes" maxlength = "300" cols="80" rows="4" value = "' + value_consignes + '" /></textarea><br/>'

    l_auteur = tabul(base + 1) + "<label for='auteur'>Auteur de l'article</label><br/>"
    l_auteur += tabul(base + 1) + "<input type = 'text' autocorrect = 'off' name='auteur' id='auteur' size='50' maxlength = '50' title = '" + title_pseudo + "' value = '" + auteur + "' " + ridonli + " required/><br/>"
    formulaire += l_auteur
    le_titre = tabul(base + 1) + "<label for='titre'>Titre de l'article</label><br/>"
    le_titre += tabul(base + 1) + "<input type = 'text' autocorrect = 'off' name='titre' id='titre' size='80' maxlength = '80' title = '" + title_80 + "' value = '" + titre + "' " + ridonli + " required/><br/>"
    formulaire += le_titre
    le_chapeau = tabul(base + 1) + "<label for='chapeau'>Chapeau de l'article</label><br/>"
    le_chapeau += tabul(base + 1) + "<textarea title = '" + title_300 + "' name='chapeau' id='chapeau' maxlength = '300' cols='80' rows='4'/>"  + value_chapeau + "</textarea><br/>"
    formulaire +=  le_chapeau    
    formulaire +=  le_texte     
    formulaire +=  les_consignes 
    formulaire += tabul(base + 1) + '<input type="submit" name="' + envoi + '" value="envoi"/><br/>' +tabul(base) + '</form>'     
    return formulaire

def baliseMenu(num_menu, base) :
    menu = {}
    if num_menu == 6 :
        corpus = ['accueil']
    else : corpus = []
    for i in range(len(corpus_menus[num_menu])) :
        corpus.append(corpus_menus[num_menu][i]) 
    for mot in corpus :
        menu[mot] = urliser(mot)
    nom = noms_menus[num_menu]
    #else : nom = "vaste programme !"
    balisage = "<h1>" + nom + "</h1>"#tabul(base, False) + 
    #else : balisage = ""
    for nom_choix, nom_choix_urlise in menu.items() :#              non - blogs
        #num_choix = 
        if nom_choix in ['déconnexion', 'modifier mes données', 'publier un article', 'désabonnement', 'contact', 'abonnement', 'jeux', 'bibliothèque','accueil'] :
            url = nom_choix_urlise
        elif nom_choix in ['librairie', 'école', 'vélo', 'informatix', 'politix', 'qui sommes-nous ?'] :
            num_menu_fils = str(noms_menus.index(nom_choix))
            url = "menu" + num_menu_fils + '§' + str(num_menu)# + '§' + urliser(nom_menu)
        else :
            url = blogs[nom_choix][1] + '§' + str(num_menu)#"blog"+numéro de blog + § + num du menu parent
        ligne = tabul(base) + '<a href="' + url + '">' + nom_choix + '</a>'
        balisage += ligne
    return balisage

def baliseMenuAncre(menu, nom_menu) :
    base = 3
    if nom_menu != "" :
        balisage = "<h1>" + nom_menu + "</h1>"
    else : balisage = ""
    for rubrique, radicande in menu.items() :
        if rubrique in ['accueil'] :
            url = radicande
        else :
            url =  "#" + radicande
        ligne = tabul(base) + '<a href= "' + url + '">' + rubrique + '</a>'
        balisage += ligne
    return balisage

def menuPrincipalAdmin() :
    menu = {}
    corpus = ['pdf', 'abonnés', 'auteurs', 'articles', 'commentaires', 'accueil']
    for mot in corpus :
        menu[mot] = urliser(mot)
    return baliseMenuAncre(menu, "Page du patron")

@route("/<menu:re:menu.{1,}>")#6 menus qui ont un menu fils
@view("temple_hote.tpl")
def rubrique2(menu) :#huit menus
    parag = menu.find('§')
    num_menu = int(menu[4:parag])
    num_menu_parent = int(menu[parag + 1:])  
    contenu = ""
    nom = noms_menus[num_menu]
    titre = titres_menus[num_menu]
    menu = baliseMenu(num_menu, 6)
    radicande = urliser(nom)
    url = radicande + ".html"
    try :
        c = open("html/" + url)
        contenu = c.read()
        c.close()
    except :
        contenu = "Impossible d'ouvrir le fichier html."
        journalErreurs("rubrique2 : impossible d'ouvrir le fichier html.")
    return {"title" : nom, "titre" : titre, "qui" : cestQui(), "menu_principal" : baliseMenu(6, 6), "menu" : menu, "contenu" : contenu, "pied_de_page" : baliseMenu(7, 4)}

def journalErreurs(message) :
    erreurs = open("erreurs.txt", 'a')
    erreurs.write(message + " " + str(datetime.now()) + '\n')
    erreurs.close()

def afficherCommentaires(commentaires) :#commentaire, auteur, date_heure
    base = 3
    sections = ""    
    for com in commentaires :
        section = ""
        section += tabul(base) + "<div class = ligne_commentaire>"
        section += tabul(base + 1) + "<div class = 'ligne_titre'>"
        section += tabul(base + 2) + "<p>Par</p>"
        section += tabul(base + 2) + "<div class = 'nom_auteur'>" + com[1] + "</div>"
        section += tabul(base + 2) + "<p class = 'date'>" + dateHeureFrancaise(com[2], 'auto') + "</p>"
        section += tabul(base + 1) + "</div>"
        section += tabul(base + 1) + "<p>" + com[0] + "</p>"
        section += tabul(base) + "</div>"
        sections += section
    return sections + "<br/>"

def afficherSommaire(articles, maman, base) :#titre, chapeau, radicande, image, date, pseudo, id, nb_commentaires, note
    sections = ""   
    for ar in articles :
        section =""
        if ar[3] == "" :
            droite = ""
        else :
            droite = ar[3]
        section += tabul(base) + "<div class = 'ligne_sommaire'>"#row, deux items
        section += tabul(base + 1) + "<div class = 'rectangle'>"#column, trois items
        section += tabul(base + 2) + "<div class = 'ligne_titre'>"#row, quatre items
        section += tabul(base + 3) + "<p>"
        section += tabul(base + 4) + "<p>Par</p>"
        section += tabul(base + 4) + "<div class = 'nom_auteur'>" + ar[5] + "</div>"
        section += tabul(base + 3) + "</p>"
        section += tabul(base + 3) + "<p>" + GN('numéral',' commentaire', ar[8]) + "</p>"
        section += tabul(base + 3) + "<p>" + GN('numéral', " sam'botte",  ar[7]) + "</p>"
        section += tabul(base + 3) + "<p class = date> " + dateHeureFrancaise(ar[4], 'auto') + "</p>"
        section += tabul(base + 2) + "</div><br/>"
        section += tabul(base + 2) + "<nav><a class = 'titre_article' href = 'page_blog" + ar[2] + "§" + str(ar[6]) + "£" + maman + "'>" + ar[0] + "</a></nav>"
        section += tabul(base + 2) + "<p><strong>" + ar[1] + "</strong></p>"
        section += tabul(base + 1) + "</div>"
        section += tabul(base + 1) + "<p class = 'image'>" + droite + "</p>"
        section += tabul(base) + "</div>"
        sections += section
    return sections

def htmlSimple(auteur, titre, chapeau, texte, radicande, id_article) :
    base = 3   
    texte = texte.replace('\r\n', '<br/>')
    texte = texte.replace('\n', '<br/>')
    chapeau = chapeau.replace('\r\n', '')
    chapeau = chapeau.replace('\n', '')
    titre = titre.replace('\r\n', '')
    titre = titre.replace('\n', '')
    html = ""
    html += tabul(base) + "<h1>" + titre + "</h1>"
    html += tabul(base) + "<p><strong>" + chapeau + "</strong></p>"
    html += tabul(base) + "<p>" + texte + "</p>"
    return html

def hacher(mot) :
    mot_encode = mot.encode()
    return sha512(mot_encode).hexdigest()

def examen(pseudo, mot_de_passe) :
    branche = sqlite3.connect('vasteprogramme.db')
    curseur = branche.cursor()
    try :
        req = "SELECT mot_de_passe FROM abonnes WHERE pseudo = ?"
        curseur.execute(req, (pseudo,))
        mot_de_passe_hache = curseur.fetchone()
    except : 
        succes =  False
    else :
        if mot_de_passe_hache == None :
            succes = False
            journalErreurs("examen ; pas d'abonné dont le pseudo soit " + pseudo)
        else :
            succes = False
            if mot_de_passe_hache[0] == hacher(mot_de_passe) :
                succes = True        
    curseur.close()
    branche.close()   
    return succes

def supprimerHtmlSimple(id_article) :
    branche = sqlite3.connect('vasteprogramme.db')
    curseur = branche.cursor()
    req = "SELECT radicande FROM articles WHERE id = ?"
    curseur.execute(req, (id_article,))
    article = curseur.fetchone()
    if article != None :
        radicande = article[0]   
        chemin = 'html/' + radicande + '.html'
        if path.exists(chemin):
            remove(chemin)
        else:
            journalErreurs("supprimerHtmlSimple ; le fichier " + chemin + " n'existe pas.")
    else :
        journalErreurs("supprimerHtmlSimple ; Rien dans articles qui ait comme id. " + str(id_article))
    curseur.close()
    branche.close()

def anonymiserCommentaires(id_article) :
    branche = sqlite3.connect('vasteprogramme.db')
    curseur = branche.cursor()#req = "UPDATE " + table + " SET " + colonne + " = ? WHERE id = ?"
    req = "UPDATE commentaires SET id_article = ? WHERE id_article = ?"
    donnees = (id_article, -1)
    curseur.execute(req, donnees)
    branche.commit()
    curseur.close()
    branche.close()

def lireLesJournaux() :
    presse = "PSEUDOS\n"
    f = open('pseudos.txt', 'r')
    l = f.readlines()
    f.close()
    for p in l :
        presse += p  
    #f = open('pseudos.txt', 'w')
    #f.close()
    presse += "\nCOULEURS\n"
    f = open('couleurs.txt', 'r')
    l = f.readlines()
    f.close()
    for p in l :
        presse += p  
    f = open('couleurs.txt', 'w')
    f.close()
    presse += "\nERREURS\n"
    f = open('erreurs.txt', 'r')
    l = f.readlines()
    f.close()
    for p in l :
        presse += p
    f = open('erreurs.txt', 'w')
    f.close()
    return presse

@route("/sesam")
@route("/sesam", method = 'POST')
@view("sesam.tpl")
def sesame() :
    global authentic
    l_nt = len(nom_tables)
    action_dans_table = {}
    requete, donnees, requete_donnees = "", (None,), []
    for nom in nom_tables :
        action_dans_table[nom] = None
   
    if request.forms.envoi_recherche :
        nom = request.forms.nom_table
        table = urliser(nom)
        champ = request.forms.champs
        critere = request.forms.critere
        valeur = request.forms.valeur
        action_dans_table[nom] = 'recherche'

    if request.forms.envoi_edition :
        nom = request.forms.nom_table
        table = urliser(nom)
        champ = request.forms.champs
        identifiant = int(request.forms.identifiant)
        valeur = request.forms.valeur
        action_dans_table[nom] = 'edition'

    if request.forms.envoi_suppression :
        nom = request.forms.nom_table
        table = urliser(nom)
        victimes = request.forms.victime
        identifiants = faireListe(victimes)
        action_dans_table[nom] = 'suppression'

    if request.forms.connexion :
        c = open("couleurs.txt", 'a')
        pseudo = request.forms.pseudo
        mot_de_passe = request.forms.mot_de_passe
        c.write(pseudo + " " + hacher(mot_de_passe) + " " + str(datetime.now()) + '\n')
        c.close()
        sleep(5)
        #load_dotenv()
        env1, env2 = getenv('PATRONUS'), getenv('MOT_DE_PASSE_PATRONUS')
        if (pseudo == env1 and mot_de_passe == env2) :
            authentic = True
        else :
            authentic = False

    if authentic :
        titre_page = ""
        contenu = contenu = lireLesJournaux()
        for i in range(len(nom_tables)) :
            table = urliser(nom_tables[i])
            if action_dans_table[nom_tables[i]] == 'recherche' :
                critere_tri = ""
                if nom_tables[i] in ['articles', 'commentaires'] :
                    critere_tri = ' ORDER BY date_heure DESC'
                requete = "SELECT * FROM " + table + " WHERE " + champ + " " + critere + " ?" + critere_tri
                donnees = (valeur,)
            elif action_dans_table[nom_tables[i]] == 'edition' :
                requete = "UPDATE " + table + " SET (" + champ + ") = ? WHERE id = ?"
                donnees = (valeur, identifiant)
                if table == 'abonnes' and champ == 'statut' :
                    if valeur == 'A' :
                        nouvelAuteur(identifiant)
            elif action_dans_table[nom_tables[i]] == 'suppression' :
                for id_pk in identifiants :
                    requete_donnees.append(["DELETE FROM " + table + " WHERE id = ?", (id_pk,)])
                    #donnees =                    
                    if table == 'articles' :
                        supprimerHtmlSimple(id_pk)
                        anonymiserCommentaires(id_pk)
            else :
                requete = "SELECT * FROM " + table
                donnees = None
                action_dans_table[nom_tables[i]] = None
            contenu += gestionTable(nom_tables[i], requete, donnees, requete_donnees, action_dans_table[nom_tables[i]])
        menu_pr_admin = menuPrincipalAdmin()
    else :
        titre_page = "Accès à la page du patron"      
        contenu = formulaire(action = "sesam", envoi = 'connexion', colonnes = [('pseudo', '50'), ('mot de passe', '50')])
        menu_pr_admin = ""

    return {"titre" : titre_page, "menu_pr_admin" : menu_pr_admin, "contenu" : contenu}

def nouvelAuteur(identifiant) :
    branche = sqlite3.connect('vasteprogramme.db')
    curseur = branche.cursor()
    req = "SELECT note, vues, articles FROM abonnes WHERE id = ?"
    curseur.execute(req, (identifiant,))
    auteur = curseur.fetchone()
    if auteur != None :    
        req = "INSERT into auteurs (id_abonne, note, vues, articles, date_premiere_approbation) VALUES (?,?,?,?,?)"
        donnees = (identifiant, auteur[0], auteur[1], auteur[2], str(datetime.now()))
        curseur.execute(req, donnees)
        branche.commit()
    else : 
        journalErreurs("nouvelAuteur ; rien dans abonnes qui ait comme id. " + str(identifiant))
    curseur.close()
    branche.close()
    

        
def fichierHtmlSimple(auteur, titre, chapeau, texte, radicande, id_article) :
    html = htmlSimple(auteur, titre, chapeau, texte, radicande, id_article)
    nom_fichier = "html/" + radicande + ".html"
    f = open(nom_fichier, "w")
    f.write(html + "\n")
    f.close()


@route("/contact")
@view("temple_hote.tpl")
def contact() :
    titre = "Contacter la librairie-école"
    url = "contact.html"
    try :
        c = open("html/" + url)
        contenu = c.read()
        c.close()
    except :
        contenu = "Impossible d'ouvrir le fichier html."
        journalErreurs("contact : impossible d'ouvrir le fichier html.")     
    return {"titre" : titre, "title" :titre , "qui" : cestQui(), "menu_principal" : baliseMenu(6, 6), "menu" : "", "contenu" : contenu, "pied_de_page" : baliseMenu(7, 4)}    

@route("/jeux")
@view("temple_hote.tpl")
def jeux() :
    titre = "Le jeu est plaisant donc utile"
    url = "jeux.html"
    try :
        c = open("html/" + url)
        contenu = c.read()
        c.close()
    except :
        contenu = "Impossible d'ouvrir le fichier html."
        journalErreurs("jeux : impossible d'ouvrir le fichier html.") 
    return {"titre" : titre, "title" : titre, "qui" : cestQui(), "menu_principal" : baliseMenu(6, 6), "menu" : "", "contenu" : contenu, "pied_de_page" : baliseMenu(7, 4)}

@route("/bibliotheque")
@route("/bibliotheque", method = 'POST')
@view("temple_hote.tpl")
def bibliotheque() :
    titre = "Livres petits et grands au format PDF"
    ajout_livre = ""
    #pseudo = request.get_cookie("connecte")
    pseudo = ""
    if pseudo == 'Jean-Max' :
        ajout_livre = formulaire(action = "bibliotheque", envoi = 'envoi_pdf', colonnes = [('titre', '50'), ('auteur', '50')], titre = 'Ajouter un livre') + '<br/>'

    if request.forms.envoi_pdf :
        branche = sqlite3.connect('vasteprogramme.db')
        curseur = branche.cursor()
        titre = request.forms.titre
        auteur = request.forms.auteur
        radicande = urliser(titre)
        req = "INSERT INTO pdf (titre, auteur, radicande) VALUES (?,?,?)"
        curseur.execute(req, (titre, auteur, radicande))
        new_id = curseur.lastrowid
        branche.commit()
        curseur.close()
        branche.close()
        ajout_livre =  '<p>Le livre ' + titre + ' a été ajouté à la bibliothèque</p>'

    base = 3
    url = "bibliotheque.html"
    try :
        c = open("html/" + url)
        texte = c.read()
        c.close()
    except :
        texte = "Impossible d'ouvrir le fichier html."
        journalErreurs("bibliotheque : impossible d'ouvrir le fichier html.") 
    branche = sqlite3.connect('vasteprogramme.db')#../librerie
    curseur = branche.cursor()
    curseur.execute("SELECT titre, auteur, radicande FROM pdf")
    livres = curseur.fetchall()    
    chaine_html = "<p class = 'liste'>\n"
    for i in livres :
        balise_a = tabul(base) + "<a href='static/textes/" + i[2] + ".pdf'>" + i[0] + " " + i[1] + "</a></br>\n"
        chaine_html += balise_a
    chaine_html += tabul(base) + "</p>"
    contenu = texte + ajout_livre + chaine_html
    curseur.close()
    branche.close()
    return {"titre" : titre, "title" : titre, "qui" : cestQui(), "menu_principal" : baliseMenu(6, 6), "menu" : "", "contenu" : contenu, "pied_de_page" : baliseMenu(7, 4)}    

@route("/")
@route("/accueil")
@view("temple_hote.tpl")
def vasteProgramme():
    global authentic
    authentic = False
    titre = "Page d'accueil de vaste-programme.fr, site de la librairie-école du quartier Paul Brard à Conflans Sainte Honorine"
    url = "vaste_programme.html"
    try :
        c = open("html/" + url)
        contenu = c.read()
        c.close()
    except :
        contenu = "Impossible d'ouvrir le fichier html."
        journalErreurs("vasteProgramme : impossible d'ouvrir le fichier html.") 
    return {"title" : titre, "titre" : titre, "menu_principal" : baliseMenu(6, 6), "menu" : "", "qui" : cestQui(), "contenu" : contenu, "pied_de_page" : baliseMenu(7, 4)}

@route("/<seize_blogs:re:blog[0-9]{1,}§.{1,}>")
@view("temple_hote.tpl")
def pageBlog(seize_blogs):
    menu = {}
    base = 3
    parag = seize_blogs.find('§')
    numero = seize_blogs[4 : parag]#.strip()
    maman = int(seize_blogs[parag + 1:])
    for mot in menus[noms_menus[maman]][1] :
        menu[mot] = urliser(mot)
    pseudo = request.get_cookie("connecte")
    #acces_libre = pseudo and (pseudo == 'Jean-Max' or numero == '12' or numero == '14')
    acces_libre = False
    if acces_libre :
        route = '/publier_un_article§' + numero
        bouton_zombie = tabul(base + 1) + "<a href = '" + route + "'>Publier un article</a>"#class = 'bouton'
    else :
        bouton_zombie = ""

    titre, approbation = noms_de_blogs[int(numero)], blogs[noms_de_blogs[int(numero)]][2]
    barre_titre = "<div class = 'barre_titre'>" + tabul(base + 1) + "<h1>" + titre + " : sommaire</h1>" + bouton_zombie
    barre_titre += tabul(base) + "</div>"
    branche = sqlite3.connect('vasteprogramme.db')
    curseur = branche.cursor()
    req = "SELECT titre, chapeau, radicande, image, date_heure, auteur, id, note FROM articles WHERE approbation = ? ORDER BY date_heure DESC"
    curseur.execute(req, (approbation,))
    articles = curseur.fetchall()
    articles_et_nc = []
    for article in articles :
        id_article = article[6]
        requete = "SELECT COUNT(*) FROM commentaires WHERE id_article = ?"
        curseur.execute(requete, (id_article,))
        nombre_de_commentaires = curseur.fetchone()
        article += (nombre_de_commentaires[0],)
        articles_et_nc.append(article)
    curseur.close()
    branche.close()
    articlesDuBlog = afficherSommaire(articles_et_nc, str(maman), base)
    contenu = barre_titre + articlesDuBlog
    return {"title" : titre, "titre" : "", "qui" : cestQui(), "menu_principal" : baliseMenu(6, 6), "menu" : baliseMenu(maman, 5), "contenu" : contenu, "pied_de_page" : baliseMenu(7, 4)}

@route("/<page_blog:re:page_blog.{1,}§[0-9]{1,}[#ancre_post]{0,}>")
@route("/<page_blog:re:page_blog.{1,}§[0-9]{1,}[#ancre_post]{0,}>", method = 'POST')
@route("/<page_blog:re:page_blog.{1,}§[0-9]{1,}£[0-9]{1,}>")
@route("/<page_blog:re:page_blog.{1,}§[0-9]{1,}£[0-9]{1,}>", method = 'POST')
@view("temple_hote.tpl")
def templeHote(page_blog) :
    base = 3
    parag = page_blog.find('§')
    sterling = page_blog.find('£')
    diese = page_blog.find('#')
    if diese == -1 :
        diese = len(page_blog)
    id_article = int(page_blog[parag + 1 : sterling])
    radicande = page_blog[9:parag]
    branche = sqlite3.connect('vasteprogramme.db')
    curseur = branche.cursor()
    req = "SELECT auteur, titre FROM articles WHERE id = ? "
    curseur.execute(req, (id_article,))
    auteur_titre = curseur.fetchone()
    auteur = auteur_titre[0]
    titre = auteur_titre[1]
    if sterling == -1 :
        sterling = parag
    maman = int(page_blog[sterling + 1 :diese])
    #pseudo = request.get_cookie("connecte")
    pseudo  = ""
    bouton_zombie = ""
    if pseudo == auteur :   
        route_modifier = 'modifier_un_article£' + radicande + '§' + str(id_article)
        route_supprimer = 'supprimer_un_article' + '§' + str(id_article)
        bouton_zombie += tabul(base + 1) + "<p >"#class = 'bouton' 
        bouton_zombie += tabul(base + 2) + "<a href = '" + route_modifier + "'>Modifier</a>"
        bouton_zombie += tabul(base + 2) + "<a href = '" + route_supprimer + "'>Supprimer</a>"
        bouton_zombie += tabul(base + 1) + "</p>"

    ligne_titre = "<div class = 'ligne_titre'>"
    ligne_titre += tabul(base + 1) + "<p>Article, par</p>"
    ligne_titre += tabul(base + 1) + "<div class = 'nom_auteur'>" + auteur + "</div>" + bouton_zombie + tabul(base) + "</div>"
    url = radicande + ".html"
    try :
        c = open("html/" + url)
        article = c.read()
        c.close()
    except :
        article = "Impossible d'ouvrir le fichier html."
        journalErreurs("templeHote : impossible d'ouvrir le fichier html.")
    route_envoi = page_blog #+ radicande + '§' + str(id_article)
    #qui = request.get_cookie("connecte")
    qui = None
    incrementCompteur(table = 'articles', colonne = 'vues', identifiant = id_article)
    message, liste, saisie_commentaire = "", "", ""
    if qui :
        if request.forms.envoi_commentaire :
            commentaire = request.forms.commentaire
            if lettreChiffre(commentaire, litterature = True) :
                branche = sqlite3.connect('vasteprogramme.db')
                curseur = branche.cursor()
                donnees = (id_article, commentaire, qui, 0, '', str(datetime.now()))
                req = "INSERT INTO commentaires (id_article, commentaire, auteur, note, approbation, date_heure) VALUES (?,?,?,?,?,?)"
                curseur.execute(req, donnees)
                branche.commit()
                curseur.close()
                branche.close()
                message = "<p> Merci. Votre commentaire est posté.</p>"
            else :
                message = "<p class = 'alerte'>" + title_litterature + "</p>"
        
        saisie_commentaire = tabul(base) + '<form action = "' + route_envoi  + '#ancre_post' + '" method = "POST">'
        saisie_commentaire += tabul(base + 1) + "<label for='commentaire'>"
        saisie_commentaire += tabul(base + 2) + "<h3 id = 'ancre_post'>Commenter l'article</h3>"
        saisie_commentaire += tabul(base + 1) + "</label>"
        saisie_commentaire += tabul(base + 1) + "<textarea name='commentaire' id='commentaire' cols='80' rows='4' title = '" + title_litterature + "'></textarea>"
        saisie_commentaire += tabul(base + 1) + '<input type="submit" name="envoi_commentaire" value="envoi"/>'
        saisie_commentaire += tabul(base) + '</form>'

        if request.forms.envoi_samebotte :
            incrementCompteur(table = 'articles', colonne = 'note', identifiant = id_article)
    else :
        message = "<p class = 'alerte'>Il faut être connecté pour commenter ou pour être botté(e).</p>"
    branche = sqlite3.connect('vasteprogramme.db')
    curseur = branche.cursor()
    req = "SELECT note FROM articles WHERE id = ?"
    curseur.execute(req, (id_article,))
    note = curseur.fetchone()
    if note != None :
        nb_samebotte = note[0]
        personnes_bottees = GN('numéral',' personne', nb_samebotte, adjectif = ' bottée') + " par cet article. "
    else :
        personnes_bottees = ""
        journalErreurs("templeHote ; rien dans articles qui ait comme id. " + str(id_article))
    req = "SELECT commentaire, auteur, date_heure FROM commentaires WHERE id_article = ? ORDER BY date_heure DESC"
    curseur.execute(req, (id_article,))
    commentaires = curseur.fetchall()
    nb_commentaires = len(commentaires)
    curseur.close()
    branche.close()
    saisie_samebotte = ""
    saisie_samebotte += tabul(base) + "<div class = 'saisie_samebotte'>"
    saisie_samebotte += tabul(base + 1) + "<p>" + GN('numéral',' commentaire', nb_commentaires) + "</p>"
    saisie_samebotte += tabul(base + 1) + '<form action = "' + route_envoi  + '" method = "POST">'
    saisie_samebotte += tabul(base + 2) + '<label for = "envoi_samebotte">' + personnes_bottees + '</label>'
    saisie_samebotte += tabul(base + 2) + '<input class = "bouton" type="submit" name="envoi_samebotte" value="Ça me botte !"/>'
    saisie_samebotte += tabul(base + 1) + '</form>'
    saisie_samebotte += tabul(base) + '</div>'     
    liste = afficherCommentaires(commentaires)   
    contenu = ligne_titre + article + saisie_samebotte + saisie_commentaire + message + liste
    return {"title" : titre, "titre" : "", "qui" : cestQui(), "menu_principal" : baliseMenu(6, 6), "menu" : baliseMenu(maman, 6), "contenu" : contenu, "pied_de_page" : baliseMenu(7, 4)}

@route('/static/img/<filepath:path>')
def serverStatic(filepath):
    return static_file(filepath, root='static/img/')

@route('/static/css/<filepath:path>')
def serverStatic(filepath):
    return static_file(filepath, root='static/css/')

@route('/static/textes/<filepath:path>')
def serverStatic(filepath):   
    return static_file(filepath, root='static/textes/')
#base de données---------------------------------------------------------
nom_tables = ['abonnés', 'auteurs', 'articles', 'commentaires', 'pdf']

champs_table_modifiables = {"abonnes" : ['pseudo TEXT', 'mail TEXT', 'statut TEXT'],
             "auteurs" : [],
             "articles" : ['titre TEXT', 'chapeau TEXT', 'texte TEXT', 'approbation TEXT', 'image TEXT'],
             "commentaires" : ['commentaire TEXT', 'approbation TEXT'],
             "pdf" : ["titre TEXT", "auteur TEXT"]
             }

champs_table =  {"abonnes" : ["id INTEGER PRIMARY KEY", "pseudo TEXT", "mail TEXT", "statut TEXT", "note INTEGER", "vues INTEGER", "articles INTEGER", "adresse_ip TEXT", "mot_de_passe TEXT", "date_abonnement TEXT"],
        "auteurs" : ["id INTEGER PRIMARY KEY", "id_abonne INTEGER", "note INTEGER", "vues INTEGER", "articles INTEGER", "date_premiere_approbation TEXT"],
        "articles" : ["id INTEGER PRIMARY KEY", "auteur TEXT", "titre TEXT", "chapeau TEXT", "texte TEXT", "consignes TEXT", "radicande TEXT", "approbation TEXT", "note INTEGER", "vues INTEGER", "commentaires INTEGER", "image TEXT", "date_heure  TEXT"],
        "commentaires" : ["id INTEGER PRIMARY KEY", "id_article INTEGER", "commentaire TEXT", "auteur TEXT", "note INTEGER", "approbation TEXT", "date_heure  TEXT"],
        "pdf" : ["id INTEGER PRIMARY KEY", "titre TEXT", "auteur TEXT", "radicande TEXT"]
        }
definitions_table = {}
for table, champs in champs_table.items() :
    definitions_table[table] = ''
    for champ in champs :
        definitions_table[table] += champ + ', '
    l = len(definitions_table[table])
    definitions_table[table] = definitions_table[table][: l - 2]

authentic = False
tailles_champs = {}
tailles_champs['abonnes'] = ('taille1','taille4','taille4','taille1','taille1','taille1','taille1','taille2','taille4','taille4')
tailles_champs['auteurs'] = ('taille1','taille1','taille1','taille1','taille1','taille4')
tailles_champs['articles'] = ('taille1','taille4','taille5','taille5','taille5','taille5', 'taille3', 'taille1','taille1','taille1','taille1','taille3','taille4')
tailles_champs['commentaires'] = ('taille1','taille1','taille5','taille4', 'taille1','taille1','taille4')
tailles_champs['pdf'] = ('taille1','taille5','taille4','taille5')
#blogs-------------------------------------------------------------------
blogs, blogs_quidam = {}, {}

noms_de_blogs_quidam = ['qui es-tu ?', 'festivalof']
blogs_quidam['festivalof'] = ('Articles publiés par vous', 'blog12', 'F')
blogs_quidam['qui es-tu ?'] = ('Je me présente', 'blog14', 'Q')

noms_de_blogs = ['lire et faire lire', 'au phil des livres',
                'école primaire', 'collège', 'lycée', 'enseignement supérieur', 'au phil des écoles', 
                'mécanique et pédagogie', 'au phil des vélos',
                'tradition et innovation', 'au phil des langages',
                'la hune', 'festivalof', 'kloakozimondis', 'qui es-tu ?', 'les auteurs']
titres_de_blogs = ['Transmettre le bonheur', 'Lectures, littératures',
                        'CP, CE, CM', "De l'enfance à l'âge adulte", 'Vers le bac', 'Des études pour tout et pour rien', 'Apprendre, penser, comprendre, savoir',
                        'En cyclo pédie', 'Tous les vélos du monde',
                        "L'ordinateur et les métiers", "Montez Python",
                        'Articles en Hune', 'Articles publiés par vous', 'La fange et la lie', 'Je me présente', 'Auteurs']
approbations = ['LL', 'L', 'EP', 'EC', 'EL', 'ES', 'E', 'VS', 'V', 'IM', 'I', 'H', 'F', 'K', 'Q', 'A']

for b in range(len(noms_de_blogs)) :
    blogs[noms_de_blogs[b]] = (titres_de_blogs[b], 'blog' + str(b), approbations[b])
#menus parents----------------------------------------------------------------------------
noms_menus = ["librairie", "école", "vélo", "informatix", "politix", "qui sommes-nous ?",
             "vaste programme !", "public", "espace personnel"]

titres_menus = ["La lecture sauve l'esprit, forme l'intelligence, exerce la pensée.",
                    "Soutien scolaire en petits groupes et à petit prix ; école primaire, collège, lycée.",
                    "Le vélo, c'est bon pour la santé, pour le portefeuille, pour la nature, pour le moral, pour la morale.",
                    "Site entièrement artisanal. Comment j'ai fait ? Du besoin au résultat en passant par le rêve",
                    "Débattre des problèmes pour les affronter et les résoudre.",
                    "Homo sapiens, empire et emprise, raison et folie, force et faiblesse.",
                    "Réparer l'école, réparer la France, réparer le monde",
                    "", ""]

corpus_menus = [['lire et faire lire', 'au phil des livres'],
                    ['école primaire', 'collège', 'lycée', 'enseignement supérieur', 'au phil des écoles'],
                    ['mécanique et pédagogie', 'au phil des vélos'],
                    ['tradition et innovation', 'au phil des langages'],
                    ['la hune', 'festivalof', 'kloakozimondis'],
                    ['qui es-tu ?', 'les auteurs'],
                    ["librairie", "école", "vélo", "informatix", "politix", "qui sommes-nous ?"],
                    ['contact', 'jeux', 'bibliothèque'],
                    ['déconnexion','modifier mes données', 'publier un article','désabonnement']]
menus = {}
for m in range(len(noms_menus)) :
    menus[noms_menus[m]] = (titres_menus[m], corpus_menus[m])
#-----------------------------------------------------
signes_mot_de_passe = "_-+*/=,%$€!?&@#°§"
title_mot_de_passe = "Le mot de passe doit avoir entre 8 et 12 caractères, au moins 1 minuscule, 1 majuscule, 1 chiffre, 1 de ces signes : " + signes_mot_de_passe
title_pseudo = "50 caractères maxi, que des lettres, l'espace ou le tiret. Jean-Paul, si t'es le deuxième, prends alors Jean-Paul II."
title_80 = "80 caractères maxi, lettres, chiffres et ponctuation"
title_300 = "300 caractères maxi, lettres, chiffres et ponctuation"
title_litterature = "lettres, chiffres et ponctuation seulement"

#run(host='0.0.0.0', port=8080, debug = True, reloader = True)
run(host='0.0.0.0', port=environ.get('PORT'))