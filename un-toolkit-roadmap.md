# UN Toolkit — Roadmap maestro

> Laboratorio modular en Python para dominar el ciclo completo de datos de una ArcGIS Utility Network.
> Construirlo es el método de aprendizaje: cada módulo enseña una capa de la experticia **y** sirve en proyectos reales.

---

## 1. Visión

**Qué es:** una herramienta modular que cubre el ciclo de vida del dato en una Utility Network (UN): ingesta multiformato → transformación/validación → análisis → entrega, más una capa de IA encima.

**Para qué:** convertirte en el ingeniero de datos de referencia para UN en una empresa de soluciones Esri — alguien que recibe datos en cualquier formato, los lleva al modelo UN con calidad demostrable, los analiza, y los entrega a terceros en el formato que pidan.

**Cómo conecta con tu meta:** es tu identidad de Data/AI Engineer aplicada al dominio geoespacial Esri. El patrón ETL que ya conocés (staging → transform → load) es exactamente la columna vertebral de esto. La Capa 6 (IA) es tu diferenciador de mercado: casi nadie combina UN + RAG.

---

## 2. Principios de diseño (transversales a todas las capas)

Estos seis principios no son un módulo aparte: se aplican dentro de cada capa. Son lo que separa al competente del excepcional.

1. **La escala es la obsesión, no un detalle.** Todo proceso se mide (tiempo, conteos, memoria), se procesa en lotes, y elige la API por costo. Documentar benchmarks: "X registros en Y tiempo, y el porqué".
2. **Cada migración es un pipeline reproducible, no clicks.** Parametrizado, versionado, logueado e idempotente (corre dos veces → mismo resultado). Dominar branch versioning (reconcile/post) con cuidado quirúrgico.
3. **Validar automáticamente, no rezar.** Chequeos reproducibles de calidad antes y después de cada carga (completitud, dominios, geometrías, topología). Es el músculo de Great Expectations, otro dominio.
4. **Entender el negocio del utility, no solo el software.** Electric, gas y water tienen físicas y reglas distintas. Traducir entre el ingeniero de red y el dato.
5. **UN + IA es la carta única.** La intersección con RAG/embeddings es el posicionamiento de baja competencia mundial. Protegerla.
6. **Hacerlo visible.** Repo documentado, aportes en Esri Community, posts técnicos, y certificaciones Esri de UN como credibilidad de mercado.

**Estándar profesional (no negociable):** todo el trabajo vive en feature branches, cada cambio va por Pull Request con título y descripción en inglés, `main` protegido. Simular un entorno 100% profesional.

---

## 3. Stack tecnológico

| Pieza | Herramienta | Por qué |
|---|---|---|
| Conexión y operaciones sobre UN | **ArcGIS API for Python** (`arcgis`) | Trabaja con colecciones de features → escala. La API correcta para volumen. |
| Datos tabulares y GIS-nativos | **Spatially Enabled DataFrame** (pandas + geometría) | Lee shapefile/gdb/Excel/feature layer directo a DataFrame. |
| CAD, formatos sucios, transformaciones pesadas | **FME** (ya lo dominás) | Rey del DWG/DGN desordenado. No reescribir en Python lo que FME hace mejor. |
| Migración Geometric Network → UN | Asset package + data mapping (arcpy.pt) | Flujo especializado de Esri. |
| Persistencia / staging propio | **PostgreSQL + Docker** | Tu casa, reutilizado de API Explorer. |
| Capa IA | **sentence-transformers + pgvector + LLM local (Ollama)** | Local: privacidad, costo cero, aprender la maquinaria. |

> Nota de licencia: consultar y trazar capas de UN vía feature service **no** requiere el Advanced Editing user type extension. Solo editar lo requiere. Podés perfilar y analizar libremente desde el inicio.

---

## 4. Arquitectura de datos (la decisión más importante del toolkit)

### El problema: la explosión N×N

Si conectaras cada formato directamente con cada otro formato, con N formatos necesitarías N×(N−1) conversores. Con 10 formatos, ~90 conversores. Inmantenible.

### La solución: modelo canónico + UN como hub

Cada formato necesita solo **dos** piezas: un **reader** (formato → estructura canónica interna) y un **exporter** (canónico → formato). Así N formatos = 2N piezas, no N². Cualquier origen llega a cualquier destino pasando por el centro, **en ambas direcciones** — si cada formato tiene reader y exporter, toda dirección funciona sin código extra.

```
   shp ─┐                                        ┌─ shp
   gdb ─┤                                        ├─ gdb
   CAD ─┤  readers     ┌───────────┐  exporters  ├─ CAD
  Excel─┤ ─────────►   │ canónico  │ ─────────►  ├─ Excel
   XML ─┤              │ + staging │             ├─ XML
 PostGIS┤              └─────┬─────┘             ├─ PostGIS
   UN ──┘                    │                   └─ UN
                             ▼
                       modelo UN  ◄── hub del negocio
```

- **Bidireccional por diseño:** cualquier formato → cualquier formato. La UN casi siempre participa (origen o destino), pero el toolkit no la exige.
- **UN → UN incluido** (escenario más exigente): replicar prod↔pruebas, migrar entre versiones del modelo, copiar subredes entre redes, mover entre Portals. Lo difícil no es copiar features: es **preservar GlobalIDs, asociaciones (connectivity/containment/attachment), topología y subnetworks**. Se reconstruyen relaciones, no solo geometrías.
- **Módulos `readers/` y `exporters/`**: extensibles, igual que las categorías del profiler de API Explorer. Sumar un formato = sumar un reader y/o exporter, sin tocar el resto.

> Patrón *hub-and-spoke* / modelo canónico: cómo piensa FME por dentro y cómo diseña un Data Engineer para evitar el caos combinatorio.

### Formatos que toca un experto (origen y destino, ambas direcciones)

- **GIS-nativos:** shapefile, file/mobile geodatabase, feature services, otros Portals/AGOL, **UN ↔ UN**
- **CAD:** DWG (AutoCAD), DGN (MicroStation)
- **Tabular:** Excel, CSV
- **Legacy Esri:** Geometric Network
- **XML y derivados:** XML Workspace Document (export nativo de geodatabase), GML (OGC), KML/KMZ, **CIM** (Common Information Model — estándar de la industria eléctrica, XML/RDF), esquemas XML custom de terceros
- **Intercambio:** GeoJSON
- **Bases espaciales:** PostGIS, Oracle Spatial, SQL Server

> **Staging**: geodatabase / Postgres como área intermedia donde se limpia y normaliza antes de cargar al destino.

---

## 5. Las capas (cada una = varias sesiones de 1 hora)

### Capa 0 — Fundamento
**Objetivo:** conectarse y navegar la UN con ArcGIS API for Python.
**Construye:** `connect.py` — objeto `GIS`, búsqueda de contenido, listado de capas.
**Principios:** #6 (repo desde el día uno).
**Entregable:** primer PR — conexión al Portal funcionando.

### Capa 1 — Profiler / Auditor
**Objetivo:** retrato completo de una red.
**Construye:** módulo que reporta domain networks, tiers, asset groups, asset types, conteos, reglas, estado de topología, dirty areas, errores. Capaz de perfilar también una fuente externa antes de migrarla.
**Principios:** #3 (base de validación), #1 (conteos/medición).
**Entregable:** reporte estructurado (JSON/HTML) del estado de una UN.

### Capa 2 — Migración + validación
**Objetivo:** traer datos de terceros (cualquier formato) al modelo UN.
**Construye:** `readers/` multiformato, mapeo de campos, carga a staging, deploy al modelo UN (asset package donde aplique), validación de topología, reporte de errores.
**Principios:** #2 (reproducible/idempotente), #3 (validación pre/post), #4 (reglas por tipo de utility).
**Entregable:** migración parametrizada que corre dos veces y da el mismo resultado, con reporte de calidad.

### Capa 3 — Tracing
**Objetivo:** análisis de red.
**Construye:** wrappers de trace (upstream, downstream, isolation, connected), trace configurations reutilizables, salida estructurada.
**Principios:** #4 (qué significa cada trace en el negocio), #1 (performance de traces en lote).
**Entregable:** módulo de análisis que responde preguntas reales de la red.

### Capa 4 — Edición masiva
**Objetivo:** reubicación de puntos y recálculos en grandes volúmenes.
**Construye:** operaciones bulk con la API que escala (colecciones, no fila por fila), manejo de branch versioning (reconcile/post), benchmarks.
**Principios:** #1 (la estrella aquí: medir y optimizar), #2 (versionado seguro).
**Entregable:** "reubiqué N puntos en T tiempo, con este enfoque y por estas razones".

### Capa 5 — Extracción / entrega
**Objetivo:** entregar a terceros en su formato, filtrando lo que no debe salir.
**Construye:** `exporters/`, export de subredes, filtros de seguridad (sin info de clientes), trace configs para extracción.
**Principios:** #2 (entregas reproducibles), #4 (qué necesita cada consumidor).
**Entregable:** paquete de entrega configurable por destino.

### Capa 6 — IA (diferenciador)
**Objetivo:** preguntarle a la red en lenguaje natural.
**Construye:** embeddings del esquema y documentación de la UN → pgvector → RAG con LLM local. Ej.: "¿qué reglas de conectividad tiene esta red?", "¿qué falta para habilitar la topología?".
**Principios:** #5 (tu carta única), #6 (lo más visible/diferenciador del portafolio).
**Entregable:** asistente RAG sobre una UN concreta.

---

## 6. Ritmo y método

- **1 hora al día** a este proyecto (la otra hora, API Explorer en paralelo).
- **Un paso a la vez**, esperando confirmación antes de avanzar.
- Cada paso se explica: el **porqué**, el **para qué**, el **cómo** (separando comandos de código), y **cómo conecta** con el todo.
- Construir → leer/entender el código → practicar → comprender a fondo.

---

## 7. Visibilidad y posicionamiento (principio #6 en acción)

- Repo `un-toolkit` en GitHub, documentado (README claro, ejemplos, benchmarks).
- Aportar respuestas útiles en Esri Community sobre problemas que resuelvas.
- Posts cortos explicando un reto técnico superado (ej. una edición masiva optimizada).
- Certificaciones Esri de Utility Network como credibilidad complementaria.

---

## 8. Checklist de progreso

- [ ] Capa 0 — Conexión al Portal (PR #1)
- [ ] Capa 1 — Profiler / Auditor
- [ ] Capa 2 — Migración + validación
- [ ] Capa 3 — Tracing
- [ ] Capa 4 — Edición masiva
- [ ] Capa 5 — Extracción / entrega
- [ ] Capa 6 — IA (RAG sobre UN)

---

*Documento vivo. Se actualiza a medida que el toolkit crece.*
