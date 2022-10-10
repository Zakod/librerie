<!DOCTYPE HTML>
<HTML>
    <HEAD>
        <META CHARSET="UTF-8" />
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
                <nav id = "profil">
                   {{!qui}}
                </nav>
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
