import reflex as rx

class State(rx.State):
    pass

# Función para mostrar una noticia
def noticia(titulo, primer_texto, imagen_url, video_url=None, segundo_texto=None, tercer_texto=None, imagen_url_segunda=None, imagen_url_tercera=None):
    return rx.box(
        
        rx.text(
            titulo,
            font_size="6xl",  
            font_weight="bold",
            color="black",
            text_align="center",
            margin_bottom="1em"
        ),

        # Imagen 1 
        rx.center(
            rx.image(src=imagen_url, width="50%", height="auto", border_radius="lg", margin_y="1em")
        ),
        
        # Primer texto (descripción)
        rx.text(
            primer_texto,
            font_size="2xl", 
            margin_bottom="1em",
            color="black",
            text_align="center",
            padding_x="2em"
        ),
        
        # Imagen 2 
        rx.center(
            rx.image(src=imagen_url_segunda, width="50%", height="auto", border_radius="lg", margin_y="1em")
        ),
        
        # Segundo texto
        rx.text(
            segundo_texto,
            font_size="2xl",
            text_align="center",
            padding_x="2em",
            margin_bottom="1em",
            color="black"
        ),

        # Imagen 3 
        rx.center(
            rx.image(src=imagen_url_tercera, width="50%", height="auto", border_radius="lg", margin_y="1em")
        ),
        
        # Tercer texto
        rx.text(
            tercer_texto,
            font_size="2xl",
            text_align="center",
            padding_x="2em",
            margin_bottom="1em",
            color="black"
        ),
        
        # Video final
        rx.center(
            rx.box(
                rx.html(
                    f'<iframe src="https://www.youtube.com/embed/{video_url.split("v=")[-1]}" width="100%" height="420" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
                ),
                width="50%",  
                height="auto",
                border_radius="lg",
                box_shadow="lg",
                padding="1em",
                margin_y="1em"
            )
        ) if video_url else None,

        padding="1.5em",
        bg="white",
        box_shadow="lg",
        border_radius="xl",
        margin_bottom="2em"
    )


def index():
    return rx.vstack(
        # Encabezado de la app
        rx.box(
            rx.text(
                "INFODEPORTES",
                font_size="6xl",
                font_weight="bold",
                color="white",
                text_align="center"
            ),
            bg="black",
            width="100%",
            padding="1.5em"
        ),

        
        noticia(
            "Argentina campeón del Mundial de Qatar 2022",
            "La Albiceleste de Lionel Messi consiguió la gloria máxima tras el triunfo por penales ante Francia en el Lusail Stadium, luego de igualar 3-3 en los 120 minutos. Jugó un enorme partido hasta el descuento de Mbappé y no mereció sufrir. El haberse impuesto en la mejor final de la historia no hizo más que inyectarle épica a una conquista trabajada, sufrida, pero cargada de mística... Y muy buen fútbol. Se trata de la tercera estrella para la Selección y la primera en el torneo para el astro rosarino que, a los 35 años, logró su gran sueño, como Maradona en 1986. El fútbol hizo justicia. La Argentina hizo justicia por botines propios. Lionel Messi tiene la foto que mereció toda su brillante carrera: con la casaca albiceleste y la Copa del Mundo en sus manos. La Selección se impuso 4-2 por penales ante Francia (tras igualar 3-3 en los 120 minutos) en el estadio Lusail y se consagró campeón del Mundial de Qatar 2022. A los 35 años, en el quinto intento del capitán (autor de dos goles; el restante de Di María), la pared se rompió.",
            "https://cloudfront-us-east-1.images.arcpublishing.com/infobae/DUOMNI7QSZBJ6SEPGBJ4LQPZCA.jpg",  # Imagen 1
            "yo0JkFMFM3A",  # Video
            "Difícilmente se haya visto mayor diferencia conceptual entre dos equipos en una final del mundo como la que se advirtió en el primer tiempo entre Argentina y Francia. Gracias a Messi, de penal, tras una infracción de Dembelé a Di María, y al propio Fideo, luego de una jugada colectiva de excelencia, la Selección tomó ventaja. Tanto fue así que Deschamps realizó dos cambios antes del primer tiempo. En la segunda parte, después del enorme desgaste del primer tiempo, llegó el tiempo de resistir. Pero sin la necesidad de que los 10 jugadores se sujetaran al travesaño rodeando a Dibu Martínez. Scaloni definió el ingreso de Acuña por Fideo superstar para obturar caminos. De Paul con su manejo de los tiempos, haciendo lo que había que hacer en cada acción, más el manejo de Mac Allister y Fernández, más las perlitas de Messi, hasta supieron arrancarles algunos “ole” a las tribunas. Pero el suspenso llegó con el penal de Otamendi a Kolo Muani. Dibu estuvo a centímetros de atajarle a Mbappé. Y, con el efecto Países Bajos, casi inmediatamente llegó el 2-2, también de Kiki, con una volea. Minuto 81. Igual que el 2-2 contra Alemania en México 86. Entonces, Maradona tomó la pelota y arengó: Ahora lo ganamos. Lo mismo se propuso la Albiceleste.",
            "Y en el segundo tiempo del alargue parecía haber llegado el premio. Fue a los 108 minutos, luego del remate furioso de Lautaro Martínez que contuvo Lloris, y del rebote que tomó la Pulga, para volver a romper el score. El guión pedía algo así, la escena épica, con el muchachito de la película, para coronar tamaña obra. No obstante, otra vez se interpuso un obstáculo. Otro penal que Mbappé tradujo en su hattrick y en el 3-3. Y en los penales llegó la gloria. Otra vez con Dibu como héroe, atajando el penal de Coman y poniendo nervioso a Tchouameni para que desviara el suyo. Fue Gonzalo Montiel el héroe que puso el 4-2 decisivo.\n\nPorque no fue un camino sencillo el de la selección argentina, tal como quedó comprobado en la final. Todo parecía marchar sobre ruedas después de la victoria 5-0 ante los Emiratos Árabes en la previa del inicio del torneo que sirvió para estirar el invicto de la Scaloneta a 36 partidos. Pero, después de aquel holgado triunfo conseguido el 16 de noviembre, Lionel Scaloni se encontró con la primera turbulencia. “Los jugadores son bastante grandecitos como para decir si están en condiciones de seguir o no”, disparó después del pitazo final y anticipó lo que ocurriría al día siguiente.",
            "https://the-ans.jp/wp-content/uploads/2022/12/19030139/20221219_argentina_reuters.jpg",  # Imagen 2
            "https://fotos.perfil.com/2022/12/18/trim/1140/641/messi-1475613.jpg"  # Imagen 3
        ),
        padding="2em",
        bg="#f7f7f7"
    )

# Configuración de la app
app = rx.App()
app.add_page(index)