<!DOCTYPE HTML>
<HTML>
    <HEAD>
        <Meta CHARSET="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href='static/css/style_article.css' />
        <link rel = "icon" href="static/img/favicon.jpg">
        <TITLE>{{!title}}</TITLE>
    </HEAD>

    <BODY>
        <header>
            <div class = "banniere">
                <div class = "menus">
                    <nav class="menu_principal">
                        {{!menu_principal}}
                    </nav>
                    <nav class="menu" >
                        {{!menu}}
                    </nav>
                </div>
                <div id = "profil">
                   <img  src = "static/img/Arcimboldo_petit.jpg" width = 60 height = 60 alt = "3/4 face"/>
                   {{!qui}}
                </div>
            </div>
            
        </header> 
            <h1>{{!titre}}</h1>
        <article>
            {{!contenu}}
            <br/> 
        </article>       
        <footer>
            <nav class = "pied_de_page">
                {{!pied_de_page}}
            </nav>
        </footer>
    </BODY>
</HTML>
