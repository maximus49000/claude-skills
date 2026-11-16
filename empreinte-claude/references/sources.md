# Sources et chiffres de comparaison

Relevé du 2026-11-16. Citer la source avec chaque chiffre repris dans un bilan.

## Méthodologie principale

- **EcoLogits** (GenAI Impact), v0.11.3 — https://ecologits.ai/latest/methodology/llm_inference/ ; estimation des modèles propriétaires : https://ecologits.ai/latest/methodology/proprietary_models/

## Mesures et estimations par requête

| Source | Chiffres clés | Périmètre / remarque |
|---|---|---|
| Google, Elsworth et al., arXiv 2508.15734 (août 2025) | Requête Gemini médiane : 0,24 Wh ; 0,03 g CO2e ; 0,26 mL d'eau | Mesure réelle, inclut CPU, machines en veille et PUE ; exclut la fabrication. Médiane : les requêtes longues ou avec raisonnement coûtent bien plus |
| Mistral AI, Carbone 4 et ADEME, ACV de Mistral Large 2 (juillet 2025) | Réponse de 400 tokens : 1,14 g CO2e ; 45 mL d'eau ; 0,16 mg Sb éq. | Seule ACV complète publiée par un fournisseur (ISO 14040/44, référentiel AFNOR). Impact ≈ proportionnel à la taille du modèle |
| Epoch AI, J. You (février 2025) | GPT-4o : ≈ 0,3 Wh (500 tokens) ; ≈ 2,5 Wh avec 10 k tokens d'entrée ; ≈ 40 Wh avec 100 k | Montre le poids du contexte long |
| Jegham et al., « How Hungry is AI? », arXiv 2505.09598 (v5, 2025) | Claude 3.7 Sonnet : 0,95 / 2,99 / 5,67 Wh (prompt court / moyen / long) | Déduit de la latence d'API ; forte incertitude |
| S. P. Couch, blog (janvier 2026) | Claude Code : session médiane ≈ 41 Wh ; journée de travail médiane ≈ 1,3 kWh | Coefficients grossiers, mais seule estimation dédiée aux agents de code |
| Li et al., « Making AI Less Thirsty », arXiv 2304.03271 | 10 à 50 mL d'eau par réponse (GPT-3) | Référence pour la distinction eau sur site / eau de production électrique |

## Cadres et rapports

- **AFNOR Spec 2314, Référentiel général pour l'IA frugale** (juin 2024) — méthode de mesure, bonnes pratiques, règles contre l'écoblanchiment.
- **AIE, Energy and AI** (avril 2025) — datacenters : 415 TWh en 2024 (≈ 1,5 % de l'électricité mondiale), ≈ 945 TWh projetés en 2030.
- **Luccioni, Jernite, Strubell, « Power Hungry Processing »** (FAccT 2024) — un modèle généraliste consomme beaucoup plus qu'un modèle spécialisé pour la même tâche.
- **AI Energy Score v2** (Hugging Face, décembre 2025) — avec le raisonnement activé, un même modèle consomme 150 à 700 fois plus (beaucoup plus de tokens générés).
- **ML.ENERGY** (Chung et al.) — base de mesure d'EcoLogits ; l'énergie varie d'un facteur 25 selon la tâche.

## Facteurs d'émission et équivalences

- Électricité USA ≈ 384 g CO2e/kWh ; monde ≈ 458–473 (Ember) ; France ≈ 52 g (ADEME Base Empreinte, ACV). Une même requête émet ≈ 7 fois moins sur le réseau français, mais les datacenters d'Anthropic sont aux USA.
- ADEME Impact CO2 (https://impactco2.fr) : voiture thermique 142 g CO2e/km (fabrication incluse) ; voiture électrique 67 g/km ; TGV 2,9 g/km ; repas végétarien 850 g ; repas avec bœuf 4,97 kg ; fabrication d'un smartphone 79 kg. Les valeurs d'un courriel et d'une heure de streaming varient selon les paramètres sur le site : ne pas les citer sans les vérifier.

## Ce que dit Anthropic

- https://www.anthropic.com/policy/infrastructure : nouvelles capacités électriques surtout au gaz naturel, avec projets géothermie, éolien, solaire ; refroidissement en circuit fermé ou à l'air ; engagement à publier des données d'émissions par site vérifiées par un tiers.
- Aucun chiffre public d'énergie ou de carbone par requête ou par token à ce jour ; pas de rapport de durabilité (Heatmap, juin 2026). Tout chiffre sur Claude est donc une extrapolation.
