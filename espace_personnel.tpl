<!DOCTYPE HTML>
<HTML>
    <HEAD>
        <meta CHARSET="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href='static/css/style_article.css' />
        <link rel = "icon" href="static/img/favicon.jpg">
        <TITLE>{{!titre}}</TITLE>
    </HEAD>

    <BODY>
        <header>
            <div class = "banniere">
                <nav class="menu_principal">
                   {{!menu_principal}}
                </nav>
                <nav id = "profil">
                    {{!qui}}
                </nav>
            </div>
            <nav class="menu">
                {{!menu}}
            </nav>
        </header> 
        <h1>{{!titre}}</h1>   
        <section>
            {{!contenu}} 
        </section>       
        <footer>
            <nav class = pied_de_page>
            {{!pied_de_page}}
            </nav>
        </footer>
    </BODY>
</HTML>
