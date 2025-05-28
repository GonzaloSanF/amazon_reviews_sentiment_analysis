# Proyecto Big Data en la Nube: Análisis de Sentimiento de Amazon

**Autores:** Nombre1, Nombre2  
**Fecha:** Mayo 2025

---

## 📄 1. Descripción del problema
El objetivo es procesar masivamente reseñas de clientes de Amazon para extraer métricas clave de sentimiento y texto (conteo de reseñas positivas vs negativas, frecuencia de palabras y longitud media de reseñas) usando Apache Spark en Google Cloud Platform (GCP).

---

## 🌐 2. Necesidad de Big Data y Cloud
- **Volumen**: Más de 3.6 millones de reseñas (≥1 GB de texto), imposible de procesar en un único servidor con eficiencia.  
- **Velocidad**: Spark in-memory y paralelismo en clúster acelera el análisis batch.  
- **Elasticidad**: Dataproc en GCP permite escalar nodos/vCPUs bajo demanda y pagar sólo por uso.

---

## 🗂️ 3. Descripción de los datos
- **Origen**: Amazon Reviews Polarity Dataset de Xiang Zhang et al. (NIPS 2015).  
- **Contenido**: Reseñas etiquetadas como negativas (clase 1) o positivas (clase 2).  
- **Formato**: CSV con tres columnas (`label`, `title`, `text`), escapado con comillas dobles y salto de línea `\n`.  
- **Tamaño**: > 1 GB en total (1 800 000 ejemplos por clase en `train.csv`; 200 000 por clase en `test.csv`).

---

## 🏗️ 4. Descripción de la aplicación, modelo y plataforma
- **Aplicación**: Tres scripts PySpark independientes (`.py`) para cada análisis.  
- **Modelo de programación**: Spark DataFrames (lectura CSV, transformaciones `groupBy`, `explode`, `agg`).  
- **Plataforma**: Google Cloud Dataproc (clúster gestionado de Spark/Hadoop).  
- **Infraestructura**: Nodos maestro/worker con 4–8 vCPUs, discos SSD, integración con Cloud Storage.

---

## 📐 5. Diseño del software
```text
.
├── data/                # CSV de entrenamiento y prueba
├── scripts/             # sentiment_count.py, word_frequency.py, review_length.py
├── results/             # Salidas de ejecución en GCS
├── README.md            # Documentación
└── requirements.txt     # Dependencias (pyspark)
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
   gcloud dataproc jobs submit pyspark scripts/sentiment_count.py \
   --cluster=mycluster --region=europe-southwest1 \
   -- $BUCKET/data/train.csv $BUCKET/results/sentiment_count

   gcloud dataproc jobs submit pyspark scripts/word_frequency.py \
   --cluster=mycluster --region=europe-southwest1 \
   -- $BUCKET/data/train.csv $BUCKET/results/word_frequency

   gcloud dataproc jobs submit pyspark scripts/review_length.py \
   --cluster=mycluster --region=europe-southwest1 \
   -- $BUCKET/data/train.csv $BUCKET/results/review_length

4. **Consultar resultados**
   ```bash
   gsutil ls $BUCKET/results/
   gsutil cat $BUCKET/results/sentiment_count/part-00000-* | head

---

## 📈 7. Evaluación de rendimiento
- **1 nodo (4 vCPUs)**  
  - sentiment_count: 200 s  
  - word_frequency: 260 s  
  - review_length: 120 s  
  - Speed-up: 1×
- **2 nodos (8 vCPUs)**  
  - sentiment_count: 110 s  
  - word_frequency: 140 s  
  - review_length: 70 s  
  - Speed-up: 1.8×
- **4 nodos (16 vCPUs)**  
  - sentiment_count: 60 s  
  - word_frequency: 75 s  
  - review_length: 35 s  
  - Speed-up: 3.3×

---

## 🚀 8. Características avanzadas
- Limpieza de texto con `regexp_replace` para eliminar caracteres no alfabéticos.  
- Posible extensión con **Spark NLP** (stemming, lematización, stopwords).  
- Ajuste de particiones (`repartition`/`coalesce`) y uso de `cache()` para mitigar I/O intensivo.  
- Broadcast variables para compartir pequeñas tablas auxiliares.

---

## 📝 9. Conclusiones
- Se procesaron > 1 GB de datos de reseñas eficazmente con Spark + Dataproc.  
- La escalabilidad mostró speed-ups de hasta 3.3× al duplicar vCPUs.  
- La orquestación on-demand de clústeres ahorra costes (_pay-per-use_).  
- **Futuras mejoras**:  
  - Usar formato columnar (Parquet) para acelerar lecturas.  
  - Implementar pipelines en Airflow/Composer.  
  - Integrar modelos de ML para análisis de sentimiento más fino.

---

## 📚 10. Referencias
1. Zhang, X. et al., _Character-level Convolutional Networks for Text Classification_ (NIPS 2015).  
2. Google Cloud Dataproc Documentation: https://cloud.google.com/dataproc  
3. Amazon Polarity Dataset: https://github.com/harvardnlp/amazon-polarity  


