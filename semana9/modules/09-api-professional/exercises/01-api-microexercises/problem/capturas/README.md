M1: SERIALIZAR, aqui vemos como controlar los datos que devuelve una API.

leaky: devuelvo un dict y se escapa todo lo interno 
public : FASTApi valida, filtra, documenta y serializa
filtered: usa response_model, cuando devuelvo otro tipo, filtra lo que no declara. 

1. ¿Qué campos aparecen en /leaky y no en /public? 
En /leaky aparecen los campos raw_score y thresholf_config, que contienen informacion interna del modelo y no aparecen en /public

2. ¿Por qué /filtered tampoco devuelve esos campos, aunque la funcion devuelve un dict con todos ellos? 
Porque utiliza response_model, que filtra la respuesta y elimina los campos que no estan definidos en el modelo de salida PublicScore

3. En /docs, abre el esquema PublicScore, ¿aparece is_reliable? 
Si, aparece ya que es uno de los campos definidos en el modelo de salida. 

Lo importante de esta parte es entender que raw_score no es un dato malo ni incorrecto. Nosotros tenemos algo como esto: 
{
  "band": "acceptable",
  "confidence": 0.83,
  "raw_score": 6.137
}

band es la clasificacion final del vino 
confidence es la confianza asociada a esa prediccion 
raw_score es un valor interno que utiliza el modelo durante el calculo 

cuando una aplicacion quiere utilizar nuestra API para mostrarle al usuario la calidad del vino, no necesita concoer raw_score. 

No significa que la APi vaya a funcioanr mal. El problema es que: 
1. estamso exponiendo informacion interna innecesaria
2. si cambiamos como calcula el modelo su raw_score, los clientes podrian depender de un dato que ya no significa lo mismo. 
3. queremos controlar exactamente que informacion ofrecemos a quienes utilizan nuestra API 

response_model nos permite decidir que campos forman parte de la respuesta publica. no elimina el raw_score del modelo ni de los caluclos. Solo impide que ese campo aparezca en la respuesta que recibe el cliente. 

---------------------
M2: ERRORES. Aquí aprendemos como responde una API cuando courre un error y como podemos hacer que todos los errores tengan el mismo formato. 

{
  "age": 30,
  "income": 1000
}

aqui el resultado es 200 ok. La API funciona y devuelve un score. 

error 422, datos de entrada incorrectos 
error 404, ruta no encontrada
error 500, error interno del servidor

| Petición | Status | `error.code` | `error.fields` |
|---|---|---|---|
| Datos correctos | 200 | — | — |
| Edad `"treinta"` | 422 | `validation_error` | `age` |
| Sin `income` | 422 | `validation_error` | `income` |
| `GET /v1/nada` | 404 | `not_found` | No aparece |
| `GET /v1/boom` | 500 | `internal_error` | No aparece |

¿Para que sirve handle_validation?
En examples/error_demo.py lo encontramos. Esta funcion sirve para controlar como responde nuestra API cuando el usuario introduce datos incorrectos. Es importante porque permite que los errores tengan una estructura comun, facilitando que otras aplicaciones puedan interpretarlos y evitando mostrar información innecesaria. 

--------------
M3. OPENAPI. AQUI APRENDEMOS COMO SE DOCUMENTAN LOS ENDPOINTS DE NUESTRA API Y AÑADIREMOS UN EJEMPLO EN SWAGGER.

¿Que es OpenApi? 
Por ejemplo, imagina que has creado una API, y se la das a otra persona. Esa persona necesita saber qué endpoints existen, que datos debe enviar y que respuestas puede recibir. 

OpenApi es una espcificacion que describe todo eso. FastAPI genera automaticamente esa documentacion a partir de nuestro codigo. 

¿Donde aparecen summary, el docstring y responses de create_score en /openapi.json?
Aparecen dentro de paths, porque OpenApi organiza la documentacion por rutas y metodos HTTP. En este caso /v1/scores es la ruta y post el metodo que utiliza. 

Dentro encontramos summary, que resume que hace el endpoint; description, que contiene la explicacion del docstring de la funcion; y response, donde se indican las posibles respuestas HTTP (200, 422 y 503)

Toda esta informacion aparce ahi porque FastApi genera automaticamente la documentacion a partir del codigo de nuestra API. 

---------------

2. Ejecutar el ejemplo minor desde Swagger
Seleccionamos el ejemplo minor en Swagger, que envía una edad de 16 años. Al ejecutarlo, la Api devuelve un error 422 porque el modelo de entrada estrablece que la edad minima es 18 años.

3. Añadir el ejemplo no_income.
Añadimos un tercer ejemplo en openapi_examples que solo contiene age: 30, sin incluir income. Al ejecutarlo desde Swagger, la API devuelve un error 422 indicando que falta un campo obligatorio. 

4. ¿Por qué fallaba el test despues de añadir no_income?
AL ejecutar los tests, uno fallaba proque comprobaba que OpenAPI tuviera exactamente dos ejemplos (valid y minor). Como habiamos añadido no_income, el test ya no coincidia con la documentación actual. 

Para solucionarlo, modificamos el assert de tests/test_examples.py para que comprobara los tres ejemplos. 

------------------------
M4. AQUI ENTENDEMOS COMO PROBAR NUESTRA API AUTOMATICAMENTE SIN TENER QUE ENTRAR EN SWAGGER Y PULSA EXCUTE CADA VEZ. 

1. Localizar el test que utiliza dependency_overrides. ¿Para qué sirve?
El test es test_dependency_override_simulates_unavailable_model. 
dependency_overrides sirve para sustituir el modelo original por uno de prueba. En este caso, simualmos que el modelo no funciona (ready=False) y comprobamos que la API devuelve un error 503. Asi podemos probar que pasa cuando falla el modelo sin tener que modificar el original. 

2. ¿Qué ocurre al quitar raise_server_exceptions=False?

Al quitarlo, falla el test test_unexpected_error_hides_secrets, porque TestClient lanza directamente la excepción de Python en lugar de permitirnos comprobar la respuesta HTTP 500.

Con raise_server_exceptions=False, podemos recibir esa respuesta y comprobar que no muestra información sensible.

3. Crear un test para comprobar income: 0.

Hemos añadido el test test_income_cero, que envía una petición con income = 0 y comprueba que la API devuelve un error 422 y que el campo incorrecto es income.

Esto nos permite comprobar automáticamente que la validación funciona, sin tener que hacer la petición manualmente desde Swagger. 