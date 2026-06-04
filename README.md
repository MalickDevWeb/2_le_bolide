# 🏎️ Le Bolide (FastAPI & Async) - Microservice IoT / Streaming

Microservice ultra-rapide conçu pour absorber une charge massive de télémétrie IoT via des WebSockets.

## 🚀 Architecture & Performances (Asynchronisme Natif)
* **Event Loop Non-Bloquante :** L'application tourne sur `uvicorn` et `uvloop`, permettant de gérer des dizaines de milliers de connexions TCP simultanées sur un seul cœur CPU sans faire exploser la RAM.
* **Sérialisation Extrême :** Remplacement du parser JSON standard de Python par `ORJSONResponse` (écrit en Rust) pour un gain de performance de sérialisation x3 à x5.
* **Validation Stricte (Pydantic v2) :** Utilisation de `ConfigDict(extra="forbid", strict=True)`. Si un IoT malicieux ou défectueux envoie un payload avec des données excédentaires, il est rejeté instantanément, préservant la mémoire du serveur d'une potentielle attaque "Fat Payload" / DDoS.

## 🛠️ Gestion Avancée des WebSockets
* `ConnectionManager` avec stockage en dictionnaire mémoire.
* Diffusion (Broadcast) asynchrone utilisant `asyncio.gather` pour envoyer les messages à tous les clients en parallèle absolu (sans boucle `for` bloquante).

## 🟢 Numérique Responsable (Green IT)
* **GZipMiddleware :** Les réponses JSON > 1 Ko sont compressées, divisant la bande passante consommée par 4. Sur des volumes Télécom/IoT colossaux, cela représente des centaines de Gigaoctets économisés par mois, réduisant drastiquement l'empreinte carbone du réseau.
