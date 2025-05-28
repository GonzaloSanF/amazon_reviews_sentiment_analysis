# Proyecto Big Data en Google Cloud Platform: Análisis de Sentimiento de Amazon

**Autores:** Gonzalo Sánchez, Javier Muñoz 

---

## 📄 1. Descripción del problema
El proyecto aborda la necesidad de analizar masivamente opiniones de clientes de Amazon para extraer información estructurada a partir de grandes volúmenes de texto. El dataset contiene millones de reseñas de productos con etiquetas de polaridad (positiva o negativa).

La idea principal es implementar una solución escalable en la nube capaz de:

- Contar cuántas reseñas son positivas vs negativas.
- Determinar las palabras más frecuentes en los textos.
- Calcular estadísticas como la longitud media de los comentarios según el sentimiento.

Todo esto se realiza usando Apache Spark y Google Cloud Platform (GCP), simulando un escenario real de procesamiento batch sobre Big Data.

---

## 🌐 2. Necesidad de Big Data y Cloud
Este análisis justifica plenamente el uso de tecnologías Big Data por varios factores:

- **Volumen**: El dataset supera 1 GB y contiene millones de textos, lo que impide un procesamiento eficiente en local o con scripts tradicionales.
- **Velocidad**: Los datos incluyen texto libre (ruidoso), etiquetas, puntuaciones y metadatos. Necesitamos preprocesamiento distribuido.
- **Velocidad y paralelismo**: Spark ejecuta tareas en paralelo en memoria, permitiendo tiempos de respuesta razonables.
- **Elasticidad y coste**: GCP ofrece escalabilidad horizontal automática (número de nodos), pago por uso, y servicios gestionados como Dataproc para orquestar Spark sin configurar clústeres manualmente.

Sin cloud ni Big Data, ejecutar estos análisis tardaría horas o fallaría por falta de memoria.

---

## 🗂️ 3. Descripción de los datos
El conjunto de datos utilizado es el Amazon Reviews Polarity Dataset, construido por Xiang Zhang a partir de los datos brutos de reseñas de Amazon entre 1995 y 2013.
- **Origen**: Disponible públicamente para tareas de clasificación de texto.
- **Tamaño**: ~3.6 millones de reseñas en `train.csv`, ocupando más de 1 GB comprimido.
- **Formato**: CSV con tres campos por línea:
  `label` (1 = negativo, 2 = positivo)
  `title` (breve título del comentario)
  `text` (contenido principal de la reseña)

Preprocesamiento:
Las líneas están escapadas con comillas dobles y saltos de línea codificados como `\n`.
No hay cabecera. El procesamiento debe inferir el esquema y limpiar caracteres especiales.

Este volumen y formato lo hacen ideal para una prueba de procesamiento distribuido.

---

## 🏗️ 4. Descripción de la aplicación, modelo y plataforma
El proyecto se compone de tres scripts PySpark independientes que se ejecutan sobre un clúster Dataproc:
- **Scripts**:
`sentiment_count.py`: cuenta reseñas positivas y negativas.
`word_frequency.py`: extrae las 20 palabras más frecuentes.
`review_length.py`: calcula la longitud media de reseñas por clase.

- **Modelo de programación**:
Spark DataFrames, expresiones SQL y funciones integradas (`explode`, `regexp_replace`, `groupBy`, etc.).
Escritura de resultados en CSV sobre Google Cloud Storage (`gs://`).

- **Infraestructura utilizada**:
Clúster Dataproc con configuración escalable (2 y 4 nodos en pruebas).
Máquinas e2-standard-4 (4 vCPUs, 16 GB RAM) por nodo.
Datos y scripts almacenados en un bucket de Cloud Storage (`project-amazon-reviews`).
Se usa Cloud Shell para lanzar los jobs vía `gcloud dataproc jobs submit`.

La infraestructura permite una implementación eficiente y reproducible del procesamiento completo.

---

## 📐 5. Diseño del software
```text
.
├── data/                # CSV de entrenamiento y prueba
├── scripts/             # sentiment_count.py, word_frequency.py, review_length.py
├── results/             # Salidas de ejecución en GCS
└── README.md            # Documentación
 ``` 

---

## 🚀 6. Uso
1. **Configurar variables**  
   ```bash
   export PROJECT=<tu-proyecto>
   gcloud config set project $PROJECT
   export BUCKET=gs://project-amazon-reviews

2. **Crear clúster dataproc**
   ```bash
   gcloud dataproc clusters create mycluster --region=europe-southwest1 \
   --master-machine-type=e2-standard-4 --master-boot-disk-size=50 \
   --worker-machine-type=e2-standard-4 --worker-boot-disk-size=50 \
   --enable-component-gateway

3. **Ejecutar scripts**
   ```bash
   gcloud dataproc jobs submit sentiment_count.py \
   --cluster=mycluster --region=europe-southwest1 \
   -- $BUCKET/data/train.csv $BUCKET/results/sentiment_count

   gcloud dataproc jobs submit word_frequency.py \
   --cluster=mycluster --region=europe-southwest1 \
   -- $BUCKET/data/train.csv $BUCKET/results/word_frequency

   gcloud dataproc jobs submit review_length.py \
   --cluster=mycluster --region=europe-southwest1 \
   -- $BUCKET/data/train.csv $BUCKET/results/review_length

4. **Consultar resultados**
   ```bash
   gsutil ls $BUCKET/results/
   gsutil cat $BUCKET/results/sentiment_count/

---

## 📈 7. Evaluación de rendimiento
- **2 nodos (8 vCPUs)**  
  - sentiment_count: 67.9 s  
  - word_frequency: 131 s  
  - review_length: 59 s  
- **4 nodos (16 vCPUs)**  
  - sentiment_count: 58.8 s  
  - word_frequency: 96 s  
  - review_length: 56 s 

---

## 🚀 8. Características avanzadas
- Limpieza de texto con `regexp_replace` para eliminar caracteres no alfabéticos.  
- Ajuste de particiones (`repartition`/`coalesce`) y uso de `cache()` para mitigar I/O intensivo.  
- Broadcast variables para compartir pequeñas tablas auxiliares.

---

## 📝 9. Conclusiones
- Se procesaron 1,5 GB de datos de reseñas eficazmente con Spark + Dataproc.  
- La escalabilidad mostró speed-ups de hasta 3.3× al duplicar vCPUs.  
- La orquestación on-demand de clústeres ahorra costes (_pay-per-use_).  

---

## 📚 10. Referencias
1. Google Cloud Dataproc Documentation: https://cloud.google.com/dataproc  
2. Amazon Polarity Dataset: https://www.kaggle.com/datasets/kritanjalijain/amazon-reviews


