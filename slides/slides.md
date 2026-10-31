# Skills: Claude limpia la ENAHO

Fuente: https://claude.ai/artifact/X7H6PUvaWKde1epsYCJNze

---

# Qué es una skill y por qué crearla en Claude Code

## 1. Skills: enséñale a Claude a limpiar la ENAHO


<sub>`cover`</sub>


Ciencia de datos con Claude Code

Una carpeta con instrucciones y un script que convierte los módulos del INEI en una base lista para analizar, siempre de la misma forma

30 min de clase · 45 min de proyecto · 15 min de presentaciones


> **Notas del expositor:** Hoy damos un paso más después de MCP. El MCP le daba datos a Claude; una skill le enseña qué hacer con ellos y cómo hacerlo siempre igual. El caso es el que todos sufrimos: limpiar la ENAHO. Al final de la sesión cada uno tendrá una skill que, desde los zip del INEI, arma una base de personas y demuestra que está bien replicando la pobreza oficial de 2024.

## 2. Noventa minutos, tres bloques


<sub>`horario`</sub>


La sesión

30

**minutos de clase**

Qué es una skill, por qué en Claude Code y el pipeline de la ENAHO

45

**minutos de proyecto**

Tres skills que limpian, grafican y mapean la ENAHO, validadas contra la pobreza oficial y probadas con y sin ellas

15

**minutos de presentaciones**

Cuatro repositorios al azar, tres minutos cada uno


> **Notas del expositor:** Les cuento el plan para que administren su tiempo. Treinta minutos míos, cuarenta y cinco de ustedes y quince para ver resultados. El proyecto está pensado para terminarse en el tiempo si trabajan con Claude Code desde el principio: no escriban el script a mano, pídanselo y revísenlo.

## 3. Pídele dos veces que limpie la ENAHO y te dará dos bases distintas


<sub>`problema`</sub>


El problema

**Otro filtro**

Una vez deja a todos los miembros; otra, solo a los residentes habituales

**Otro peso**

Una vez pondera con el factor de expansión; otra, cuenta encuestas

**Otra llave**

Una vez lee el ubigeo como texto; otra, como número, y pierde los ceros

Cada respuesta parece razonable. Juntas dan cifras de pobreza que no cuadran. Una skill fija las decisiones una vez.


> **Notas del expositor:** Este es el problema real. Claude es bueno limpiando datos, pero cada conversación empieza de cero y toma decisiones distintas. En un análisis serio eso es inaceptable: necesito que el filtro, el factor y las llaves sean siempre los mismos, y que cualquiera de mi equipo obtenga la misma base. Eso es lo que resuelve una skill.

## 4. Una carpeta que Claude abre solo cuando la necesita


<sub>`que-es`</sub>


Qué es una skill

```
.claude/skills/limpiando-enaho/
├── SKILL.md     qué hace y cuándo
├── reference.md se lee si hace falta
└── scripts/
    └── limpiar.py se ejecuta
```

Proyecto

```
.claude/skills/
```

Va en el repo: todo el equipo la usa

Personal

```
~/.claude/skills/
```

Solo tú, en todos tus proyectos

Plugin

```
/plugin:skill
```

Empaquetada para instalar


> **Notas del expositor:** Una skill no es magia: es una carpeta. El único archivo obligatorio es SKILL.md, con instrucciones en Markdown. Al lado pueden ir documentos de referencia y scripts. La diferencia clave: el script se ejecuta, no se lee, así que el código no gasta contexto. Para un proyecto de datos la ponemos en .claude/skills del repositorio, porque así viaja con git y todo el equipo usa exactamente la misma limpieza. Si hay dos con el mismo nombre, gana la personal sobre la del proyecto.

## 5. Dos campos arriba, las instrucciones abajo


<sub>`skill-md`</sub>


Anatomía de SKILL.md

```
---
name: limpiando-enaho
description: Limpia módulos de la ENAHO del INEI y arma una base de personas. Úsala cuando pidan limpiar, unir o calcular pobreza con la ENAHO.
---
# Limpiar la ENAHO
1. Corre scripts/limpiar.py
2. Revisa validacion.txt
3. Para otras variables, lee reference.md
```

name

Minúsculas, números y guiones; hasta 64 caracteres. Será el comando /limpiando-enaho

description

Qué hace y cuándo usarla. Es lo único que Claude lee para decidir si la activa

El cuerpo

Pasos en Markdown; menos de 500 líneas


> **Notas del expositor:** El archivo empieza con un bloque YAML entre tres guiones. En Claude Code todos los campos son opcionales, pero description es la que importa: si falta o es vaga, Claude nunca sabrá cuándo usarla. El name, por defecto, es el nombre de la carpeta. La documentación recomienda nombres en gerundio, como limpiando-enaho, y prohíbe usar las palabras anthropic o claude. El cuerpo son instrucciones normales; la recomendación oficial es mantenerlo bajo 500 líneas y mover el detalle a otros archivos.

## 6. Claude lee la skill en tres niveles, no toda de golpe


<sub>`carga`</sub>


Fuente: documentación de Agent Skills, platform.claude.com y code.claude.com

Carga progresiva

1 · Siempre

**name y description**

Unos 100 tokens por skill, desde que abres Claude Code

2 · Al activarse

**El cuerpo de SKILL.md**

Menos de 5 mil tokens, solo cuando la tarea lo pide

3 · Si hace falta

**Referencias y scripts**

Nada hasta que se usan. Del script solo entra lo que imprime

Por eso pueden tener decenas de skills instaladas sin llenar el contexto.


> **Notas del expositor:** Este es el concepto técnico más importante. Claude no lee todas las skills al inicio: solo ve el nombre y la descripción de cada una, unos cien tokens. Cuando un pedido coincide con una descripción, carga el cuerpo de esa skill. Y los archivos de apoyo los abre solo si los necesita. Con los scripts es aún mejor: los ejecuta, y al contexto entra solo la salida, no las cien líneas de pandas. Eso hace que una skill sea más barata y más confiable que pegar un prompt larguísimo.

## 7. Claude la activa solo, o tú la llamas con /


<sub>`invocar`</sub>


Cómo se usa

**Sola**

```
¿Cuál fue la pobreza en Cusco en 2024?
```

El pedido coincide con la description y Claude carga la skill

**A mano, con argumentos**

```
/limpiando-enaho 2024
```

En el cuerpo, $ARGUMENTS o $0 se reemplaza por 2024

Campo

Para qué

disable-model-invocation: true

Solo tú la llamas; útil para lo que borra o publica

user-invocable: false

Solo Claude la usa; no aparece en el menú /

allowed-tools

Herramientas que no piden permiso mientras corre


> **Notas del expositor:** Hay dos caminos. Por defecto, Claude decide solo cuándo usarla según la descripción. O la llaman ustedes escribiendo barra y el nombre, y pueden pasarle argumentos, que dentro del archivo se leen con $ARGUMENTS o con $0, $1. Los comandos de barra que quizá conocen ya se fusionaron con las skills: un archivo en .claude/commands sigue funcionando, pero lo nuevo se hace como skill. Para ver cuáles tienen, escriban /skills o pregúntenle a Claude qué skills hay. Si editan SKILL.md, Claude Code toma el cambio sin reiniciar.

## 8. Decide si la skill se usa o se queda dormida


<sub>`description`</sub>


La description

Vaga · no se activa

```
Ayuda con datos.
```

```
Puedo limpiar tu base.
```

Específica · se activa cuando debe

```
Limpia los módulos 34 y 02 de la ENAHO del INEI y arma una base de personas con pobreza y factor de expansión. Úsala cuando pidan limpiar, unir o analizar la ENAHO, o calcular pobreza por región.
```

En tercera persona. «Limpia…», no «Puedo…»

Qué y cuándo. La acción y las situaciones de uso

Las palabras del usuario. ENAHO, pobreza, INEI

Hasta 1,024 caracteres. Si no se activa: agreguen palabras clave. Si se activa de más: sean más específicos.


> **Notas del expositor:** Este es el error número uno. La description se inyecta en el contexto de Claude, por eso la documentación pide escribirla en tercera persona. Debe decir qué hace y cuándo usarla, con las palabras que usaría alguien al pedirlo: ENAHO, INEI, pobreza, región. Hoy van a medir esto: si su skill se activa o no ante tres pedidos distintos. Si no se activa, el problema casi siempre está aquí.

## 9. Un prompt en el chat se pierde; una skill en el repo se revisa, se prueba y se hereda


<sub>`por-que-code`</sub>


Por qué en Claude Code

**Versionada con git**

Va en .claude/skills/; los cambios se revisan en un pull request

**Corre en su máquina**

Usa su entorno de uv, sus archivos y su internet; la API las corre sin red ni paquetes nuevos

**Reproducible**

El script decide lo mismo cada vez; el equipo obtiene la misma base

**Se puede evaluar**

claude -p corre los mismos pedidos con y sin la skill, en lote

**Se combina**

Con MCP, hooks y subagentes (context: fork) en el mismo proyecto

**Estándar abierto**

Sigue Agent Skills: la misma carpeta se sube a claude.ai como zip


> **Notas del expositor:** ¿Por qué hacerlo en Claude Code y no pegando un prompt en el chat? Primero, la skill vive en el repositorio: se versiona con git, se revisa en pull requests y el que llega nuevo al equipo la hereda. Segundo, corre en su máquina, con su entorno, sus datos y su internet; en la API de Claude las skills corren en un contenedor sin red y sin poder instalar paquetes, y la ENAHO hay que bajarla. Tercero, el script hace que la limpieza sea idéntica cada vez. Cuarto, se puede evaluar con claude -p, que es lo que harán hoy. Quinto, se combina con lo que ya vimos: el MCP del BCRP, hooks y subagentes. Y sexto, es un estándar abierto, Agent Skills, así que no quedan amarrados: la misma carpeta se puede subir a claude.ai. Ojo: las skills no se sincronizan solas entre Claude Code y claude.ai; cada superficie tiene las suyas.

## 10. Lo que no se discute va en el script; el criterio, en el texto


<sub>`libertad`</sub>


Script o instrucción

Puente angosto · poca libertad

```
Corre exactamente:
uv run scripts/limpiar.py
```

- Llaves como texto

- Filtro de residentes habituales

- Unión de personas y hogares

- Validación contra el INEI

Campo abierto · mucha libertad

```
Responde la pregunta con la base limpia
```

- Qué variable agregar

- Qué tabla o gráfico mostrar

- Cómo explicar el resultado

- Qué advertir al usuario


> **Notas del expositor:** La guía de buenas prácticas de Anthropic habla de grados de libertad. Si el camino es un puente angosto con precipicios a los lados, denle a Claude un script exacto y díganle que lo corra tal cual. Si es un campo abierto, denle criterios y déjenlo decidir. En limpieza de datos, las decisiones metodológicas no se discuten: llaves, filtro, unión y validación van en el script. Lo que cambia con cada pregunta, va en instrucciones. Además, el script ahorra contexto: solo su salida entra a la conversación.

## 11. Seis tipos de skills que la gente comparte


<sub>`tipos`</sub>


Lo que ya existe

**Documentos**

```
xlsx · docx · pptx · pdf
```

**Datos y estadística**

```
explore-data · validate-data · statsmodels
```

**Forma de trabajar**

```
systematic-debugging · writing-plans
```

**Diseño**

```
frontend-design · theme-factory
```

**Plataformas**

```
mcp-builder · claude-api · huggingface-datasets
```

**Crear skills**

```
skill-creator · writing-skills
```

Antes de instalar, lean el SKILL.md y sus scripts. Una skill ejecuta código en su máquina. La documentación recomienda usar solo las propias o las de Anthropic, y las estrellas no bastan: hay repos de 2026 con cientos de miles que no cuadran.


> **Notas del expositor:** Para que vean que esto ya es un ecosistema. Hay skills para documentos, que son las oficiales de Anthropic para Excel, Word, PowerPoint y PDF. Hay de datos y estadística, que son las que más nos interesan: el plugin data de Anthropic trae explore-data y validate-data, que es casi lo que harán hoy. Hay skills de forma de trabajar, como depurar de forma sistemática o escribir un plan antes de programar. De diseño, de plataformas como Hugging Face o la API de Claude, y skills para crear skills. Una advertencia seria: una skill puede traer scripts que se ejecutan en su computadora. Léanla antes de instalarla. Y no se guíen por las estrellas: en GitHub hay repositorios creados este año con más estrellas que el de Anthropic, y eso no es creíble.

## 12. Siete repositorios para explorar


<sub>`explorar`</sub>


Para explorar

Repositorio

★

Qué tiene para ustedes

[anthropics/skills](https://github.com/anthropics/skills)

185.7k

Las oficiales: xlsx, docx, pptx, pdf y skill-creator

[anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins)

34.1k

Plugin data: explore-data, validate-data, sql-queries

[K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills)

55.5k

177 de ciencia: EDA, statsmodels, scikit-learn, geopandas

[huggingface/skills](https://github.com/huggingface/skills)

11.2k

Datasets, entrenar LLM, modelos locales y Gradio

[obra/superpowers](https://github.com/obra/superpowers)

309.7k

Cómo trabajar: depurar, planes, TDD, writing-skills

[ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)

78.4k

Lista curada, por categoría

[VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)

36.7k

Más de mil skills de equipos oficiales y comunidad

```
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
claude plugin marketplace add anthropics/knowledge-work-plugins
```

Estrellas al 31 de octubre de 2026. Cada nombre abre el repositorio; los comandos de instalación están en su README.


> **Notas del expositor:** Estos son los repositorios que les recomiendo explorar durante el proyecto o en casa; cada nombre es un link. Los dos de Anthropic son la referencia: anthropics/skills tiene las skills de documentos y skill-creator, que es una skill para crear skills; knowledge-work-plugins tiene el plugin data, con validate-data, que les sirve de inspiración para hoy. K-Dense tiene 177 skills científicas, varias de estadística y ciencia de datos. Hugging Face tiene las suyas para datasets y entrenamiento. Superpowers es el más popular de forma de trabajar. Y las dos listas awesome sirven para buscar por tema. Para instalar las de Anthropic en Claude Code basta con agregar el repositorio como marketplace y luego instalar el plugin. Las de K-Dense se instalan con npx skills add o con gh skill install, según su README.

---

# El pipeline para limpiar la ENAHO y cómo validarlo

## 13. Dos módulos bastan para hoy


<sub>`enaho`</sub>


966 es el código de la ENAHO 2024 en el portal de microdatos del INEI. Cada zip trae el diccionario en PDF.

Los datos · ENAHO 2024

Módulo

Archivo

Una fila por

Filas

Llaves

Factor

34 · Sumaria

sumaria-2024.dta

hogar

33,691

conglome, vivienda, hogar

factor07

02 · Miembros

enaho01-2024-200.dta

persona

117,721

las tres + codperso

facpob07

**En la sumaria**

pobreza 1 extremo, 2 no extremo, 3 no pobre · mieperho miembros · ubigeo · estrato · dominio

**En miembros**

p203 parentesco · p204–p206 residencia · p207 sexo · p208a edad

```
proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo34.zip
proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo02.zip
```


> **Notas del expositor:** La ENAHO viene en módulos. Hoy usamos dos. La sumaria tiene una fila por hogar, con el gasto, el ingreso y la condición de pobreza ya calculada por el INEI. El módulo 200 tiene una fila por persona, con sexo, edad y si vive en el hogar. Las llaves son conglomerado, vivienda y hogar; para personas se suma codperso. Los factores de expansión son distintos: factor07 para hogares y facpob07 para personas. Los links bajan los .dta directo del INEI; cada zip pesa entre 6 y 16 MB. Ábranlos en el navegador y descomprímanlos en una carpeta datos/ que no suben a GitHub.

## 14. Siete pasos, siempre en el mismo orden


<sub>`pipeline`</sub>


El pipeline · scripts/limpiar.py

1

Leer

```
read_stata(convert_categoricals=False); llaves como texto
```

2

Normalizar

```
columnas en minúscula; «aÑo» pasa a anio
```

3

Filtrar

```
residentes: (p204==1 & p205==2) | (p204==2 & p206==1)
```

4

Unir

```
personas.merge(sumaria, on=LLAVES, validate="m:1")
```

5

Construir

```
departamento = ubigeo[:2] · urbano = estrato ≤ 5 · pobre = pobreza ≤ 2
```

6

Validar

```
llaves únicas · ninguna fila perdida · pobreza = 27.6 %
```

7

Guardar

```
salidas/personas_2024.parquet + validacion.txt
```


> **Notas del expositor:** Este es el corazón técnico. Paso uno: leer los .dta sin convertir las etiquetas, para quedarnos con los códigos, y con las llaves como texto. Dos: normalizar los nombres, porque el año viene como aÑo, con la eñe rota. Tres: quedarnos con los residentes habituales, que es la definición del INEI: miembros que no estuvieron ausentes 30 días o más, y no miembros que estuvieron presentes 30 días o más. Cuatro: unir personas con su hogar, diciéndole a pandas que es muchos a uno; si no lo es, falla en vez de duplicar filas en silencio. Cinco: construir variables. Seis: validar. Siete: guardar la base y un archivo de validación que Claude leerá. Este script se lo van a pedir a Claude Code, pero el orden y las reglas son estas.

## 15. Lo que la skill debe saber de memoria


<sub>`trampas`</sub>


Seis trampas · vistas en la ENAHO 2024

**Ceros a la izquierda**

conglome «015009», ubigeo «010101». Como número pierden el cero y la unión falla

**Nombres rotos**

La columna del año llega como «aÑo». Normalicen los nombres antes de usarlos

**No todos son residentes**

117,721 filas en el módulo 200; residentes habituales, 108,664

**Uniones que duplican**

Sin validate="m:1", un hogar repetido multiplica personas sin avisar

**Encuestas no son personas**

33,691 hogares representan 34.5 millones de personas con su factor

**Códigos, no números**

pobreza 1, 2 y 3 son categorías: pobre es pobreza ≤ 2, nunca un promedio


> **Notas del expositor:** Estas seis trampas las encontré en los archivos de 2024, no son teóricas. Las llaves vienen como texto con ceros; si alguien las convierte a número, el ubigeo 010101 se vuelve 10101 y la unión con otra fuente falla. La columna del año llega con la eñe rota. Hay unas nueve mil personas en el módulo 200 que no son residentes habituales. Una unión sin validar puede duplicar filas sin error. Sin factor de expansión, 33 mil hogares no dicen nada sobre 34 millones de personas. Y pobreza es un código. Cada una de estas reglas va en el script o en reference.md, y es exactamente lo que no queremos que Claude decida distinto cada vez.

## 16. Si su base replica la cifra oficial del INEI, está bien limpia


<sub>`validar`</sub>


La prueba

27.6 %

Pobreza monetaria 2024. Con la sumaria sale 27.58 %

5.5 %

Pobreza extrema, pobreza = 1

108,664

Residentes habituales en la base de personas

```
assert not personas.duplicated(LLAVES_PERSONA).any()
assert len(base) == len(personas) # la unión no perdió ni duplicó filas
assert abs(pobreza - 27.6) < 0.1 # cifra oficial del INEI, 2024
```

Ponderando con factor07 × mieperho en la sumaria. Con la base de personas y facpob07 sale 27.53 %.


> **Notas del expositor:** Esta es la parte que hace profesional el trabajo. No basta con que el script corra: tiene que demostrar que la base está bien. La forma más simple es replicar la cifra oficial. Yo lo corrí esta mañana con los archivos de 2024: la sumaria ponderada por factor07 por miembros del hogar da 27.58 %, y el INEI publicó 27.6 %. La pobreza extrema da 5.5 %. Si su script da otra cosa, algo filtraron o unieron mal. Estas tres líneas de assert van al final del script, y su resultado se escribe en validacion.txt, que la skill le pide a Claude leer antes de responder.

## 17. La skill completa cabe en una pantalla


<sub>`demo`</sub>


Demo · .claude/skills/limpiando-enaho/SKILL.md

```
---
name: limpiando-enaho
description: Limpia los módulos 34 (sumaria) y 02 (miembros) de la ENAHO del INEI y arma una base de personas con pobreza y factor de expansión. Úsala cuando pidan limpiar, unir o analizar la ENAHO, o calcular pobreza por región, sexo o edad.
argument-hint: [año]
---
# Limpiar la ENAHO
1. Si faltan los zip en datos/, pide al usuario bajarlos del INEI (código 966 = 2024).
2. Corre exactamente: uv run ${CLAUDE_SKILL_DIR}/scripts/limpiar.py --anio $0
3. Lee salidas/validacion.txt. Si la pobreza difiere del INEI en más de 0.1 puntos, detente.
4. Responde con salidas/personas_$0.parquet; toda cifra va ponderada con facpob07.
5. Antes de usar una variable que no está en la base, lee reference.md.
```


> **Notas del expositor:** Así se ve la skill terminada. Noten tres cosas. La description dice qué hace y cuándo, con las palabras ENAHO, INEI, pobreza y región. El paso 2 no deja libertad: corre exactamente el script; CLAUDE_SKILL_DIR es la carpeta de la skill y $0 es el año que le pasan con /limpiando-enaho 2024. Y el paso 3 obliga a Claude a revisar la validación antes de responder: si la pobreza no cuadra, se detiene en vez de inventar. En vivo: abro Claude Code en el repo, escribo /limpiando-enaho 2024 y luego pregunto la pobreza de Cusco, sin barra, para ver que se activa sola.

---

# El proyecto: tres skills para limpiar, graficar y mapear, y 15 minutos de presentaciones

## 18. Tres skills que limpian, grafican y mapean la ENAHO


<sub>`proyecto`</sub>


El proyecto · 45 minutos

Que cualquiera clone su repositorio, pida «un mapa de la pobreza por departamento» y Claude use sus tres skills, con la pobreza oficial replicada

En parejas o solos · con Claude Code · entrega en el [issue #200](https://github.com/d2cml-ai/Data-Science-Python/issues/200)

```
[github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/16-skills-enaho](https://github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/16-skills-enaho)
```


> **Notas del expositor:** Este es el proyecto. No es una skill, son tres que trabajan juntas: una limpia, otra grafica y otra hace mapas. Tienen 45 minutos, así que trabajen en parejas si pueden y pídanle todo a Claude Code: su trabajo es dirigir, revisar y validar. La prueba de que la limpieza está bien es la cifra de pobreza. La prueba de que las skills sirven es que se activen solas y cambien la respuesta frente a no tenerlas.

## 19. Cada una hace una cosa y le pasa su salida a la siguiente


<sub>`tres-skills`</sub>


Las tres skills

```
limpiando-enaho
```

Entra

Los zip 966-Modulo34 y 966-Modulo02

Sale

```
salidas/personas_2024.parquet
salidas/validacion.txt
```

```
graficando-enaho
```

Entra

La base limpia y una pregunta: pobreza por área, sexo o edad

Sale

```
figuras/*.png
```

```
mapeando-enaho
```

Entra

La base limpia y los límites de los 25 departamentos

Sale

```
mapas/pobreza_departamento.png
```

Se encadenan solas. En graficando y mapeando escriban: «Si no existe salidas/personas_2024.parquet, usa primero la skill limpiando-enaho». Así un solo pedido activa dos skills.

Inspírense en las skills matplotlib, seaborn y geopandas de K-Dense-AI/scientific-agent-skills.


> **Notas del expositor:** Las tres skills dividen el trabajo como lo haría un equipo. La primera ya la vimos: limpia y valida. La segunda toma la base limpia y hace gráficos, siempre con las mismas reglas. La tercera hace mapas por departamento. Lo interesante es que se pueden encadenar: si en la skill de mapas le dicen que, si no existe la base limpia, use primero la skill de limpieza, entonces un solo pedido, como «hazme un mapa de pobreza», activa dos skills en orden. Eso es lo que van a mostrar en la presentación.

## 20. Las reglas de gráficos y mapas van en la skill, no en cada pedido


<sub>`reglas-viz`</sub>


Qué deben fijar

**graficando-enaho**

**mapeando-enaho**

- Une por código: ubigeo[:2] con FIRST_IDDP

- Nunca por nombre: «APURIMAC» no es «Apurímac»

- Exige 25 departamentos y ninguno sin dato

- Un color de claro a oscuro, desde 0; nunca arcoíris

- Leyenda con la unidad: % de personas

- Lima (15) y Callao (07) van separados

```
raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson
```

- Pondera siempre con facpob07

- Barras que empiezan en cero, ordenadas

- Un solo color; el valor escrito en cada barra

- El título dice qué y cuándo

- Nota al pie: «Fuente: INEI, ENAHO 2024»

- PNG a 200 dpi en figuras/


> **Notas del expositor:** Igual que con la limpieza, las decisiones de diseño no se discuten en cada pedido: se fijan en la skill. Para gráficos: ponderar, barras desde cero, un solo color, el valor escrito, título y fuente. Para mapas, la trampa principal es unir por nombre: el GeoJSON trae los nombres en mayúsculas y sin tildes, y la ENAHO no trae nombres, trae ubigeo. Se une por código: los dos primeros dígitos del ubigeo con el campo FIRST_IDDP del GeoJSON. La skill debe exigir que salgan los 25 departamentos con dato. Y la escala de colores es de un solo tono, de claro a oscuro, empezando en cero; un arcoíris inventa saltos que no existen. El GeoJSON de los departamentos está en el repo del curso, en el link de abajo; pesa 140 KB.

## 21. Si su mapa da otras cifras, revisen la unión


<sub>`ejemplo-mapa`</sub>


Así debe salir · ENAHO 2024

Más pobreza

Cajamarca 45.0 % Loreto 43.0 % Puno 39.9 %

Menos pobreza

Ica 6.0 % Moquegua 11.0 % Madre de Dios 11.1 %

Calculado con la sumaria, ponderando con factor07 × mieperho, y unido por código: los 25 departamentos tienen dato.


> **Notas del expositor:** Este es el mapa que hice esta mañana con los datos reales, para que tengan contra qué comparar. La pobreza va de 6 % en Ica a 45 % en Cajamarca. Si su mapa muestra un departamento en blanco, la unión falló, casi siempre porque unieron por nombre o porque el código perdió el cero. Si las cifras no coinciden, revisen que estén ponderando. Pueden usar estas seis cifras como asserts dentro de la skill de mapas.

## 22. Cuatro pasos con reloj


<sub>`pasos`</sub>


Los 45 minutos

0–8

**Preparar**

Repo, uv init y uv add pandas pyarrow geopandas matplotlib. Bajen los dos zip y el GeoJSON a datos/

8–20

**Limpiar**

limpiar.py y la skill limpiando-enaho, hasta que la validación dé 27.6 %

20–32

**Graficar y mapear**

graficando-enaho y mapeando-enaho, cada una con su script y sus reglas

32–45

**Evaluar y subir**

Tres pedidos con y sin skills, README, push y link en el issue

```
Crea la skill mapeando-enaho: un script que lee salidas/personas_2024.parquet, calcula la pobreza ponderada por departamento, la une al GeoJSON por código y guarda mapas/pobreza_departamento.png. # un buen pedido
```


> **Notas del expositor:** Tres skills en 45 minutos es posible solo si Claude Code escribe y ustedes dirigen. Si a los 20 minutos la limpieza no da 27.6 %, sigan igual con las otras dos y anoten en el README qué falta. Para la skill de mapas pueden copiar el pedido de abajo. Pueden pedirle a Claude que use skill-creator si la instalaron, o simplemente que cree la carpeta .claude/skills con su SKILL.md y su script. La carpeta datos/ no se sube.

## 23. Tres pedidos, con y sin skills


<sub>`evaluar`</sub>


Evaluar las skills

Pedido

Skills que se activaron

Lo que debe salir

¿Cuál fue la pobreza en Cusco en 2024?

limpiando

18.5 %

Grafica la pobreza urbana y rural

graficando (+ limpiando)

24.8 % y 39.3 %

Haz un mapa de la pobreza por departamento

mapeando (+ limpiando)

Cajamarca 45.0 %, Ica 6.0 %

```
claude -p "Haz un mapa de la pobreza por departamento con la ENAHO 2024" # con skills
claude -p --disallowedTools Skill "Haz un mapa de la pobreza…" # sin skills
```

Anoten qué skills se activaron, la cifra, si ponderó y cómo se ve la figura. Si una no se activó, mejoren su description.

Referencias calculadas con la sumaria 2024, ponderando con factor07 × mieperho.


> **Notas del expositor:** La guía de Anthropic dice: crea evaluaciones antes de pulir la skill, y compara contra no tenerla. Eso hacemos con claude -p. Con la opción disallowedTools Skill, Claude no puede usar ninguna skill, y ese es el punto de comparación. Los tres pedidos prueban una skill cada uno, y los dos últimos prueban además el encadenamiento: si la base limpia no existe, deberían activar primero limpiando-enaho. En la tercera columna está lo que deben obtener; lo calculé con los datos reales. Si sin skills Claude no pondera, une por nombre o usa un arcoíris, ahí está la evidencia de que sus skills sirven.

## 24. Un repositorio que cualquiera clona y obtiene la misma base, gráficos y mapa


<sub>`entrega`</sub>


Entrega y presentaciones

```
.claude/skills/
  limpiando-enaho/ · graficando-enaho/
  mapeando-enaho/ # SKILL.md + scripts/
salidas/validacion.txt · figuras/ · mapas/
evaluacion.md · README.md · pyproject.toml
```

Rúbrica

Puntos

Limpieza: valida 27.6 % y 108,664 personas

6

graficando-enaho con sus reglas

4

mapeando-enaho: une por código, 25 con dato

4

Tres pedidos con y sin skills

4

README

2

**15 minutos: 4 repos al azar**

Tres minutos cada uno. Muestren:

- Su mapa y un gráfico

- Su validacion.txt

- Un pedido que activó dos skills seguidas

Push y link en el [issue #200](https://github.com/d2cml-ai/Data-Science-Python/issues/200) antes del sorteo.


> **Notas del expositor:** Esto es lo que entregan: las tres skills con sus scripts, la validación, las figuras, el mapa, una tabla con los tres pedidos y un README que diga cómo bajar los datos y correr todo. En los quince minutos finales sorteo cuatro repositorios; cada uno tiene tres minutos para mostrar su mapa y un gráfico, su validación y un pedido en el que se activaron dos skills seguidas. El link va en el issue 200 del repo del curso, con la plantilla que está ahí, antes del sorteo.
