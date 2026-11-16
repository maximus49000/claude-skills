# Méthodologie de calcul (EcoLogits, reproduite dans `scripts/empreinte.py`)

Source : EcoLogits v0.11.3 (GenAI Impact), https://ecologits.ai/latest/methodology/llm_inference/ et code source `ecologits/impacts/llm.py`, `ecologits/tracers/utils.py`. Relevé du 2026-11-16.

## Principe

Impact d'une requête = impact d'usage (électricité consommée × facteurs du mix électrique) + part de la fabrication du matériel (au prorata du temps d'utilisation sur 3 ans de durée de vie). Calculé pour chaque requête API, puis sommé.

Seuls les **tokens générés** (sortie, réflexion incluse) entrent dans le calcul EcoLogits. Les tokens d'entrée et le cache ne sont pas comptés : c'est la principale sous-estimation pour l'usage agentique de Claude Code.

## Formules (unités du code)

Pour un modèle de paramètres actifs `P` (milliards), `N` tokens générés, batch `B = 64` :

- Énergie GPU par token et par GPU : `f_E = (1,1665e-6 × e^(−0,011206 × B) × P + 4,0529e-5)` Wh
- Nombre de GPU (H100 80 Go, 16 bits) : mémoire = `1,2 × P_total × 16 / 8` Go → arrondi à la puissance de 2 supérieure de `mémoire / 80`
- Latence : `ttft + N / tps` (valeurs par modèle dans `ecologits_data.json`)
- Énergie serveur hors GPU : `latence/3600 × 1,2 kW × (GPU/8) / B`
- Énergie IT : `serveur + GPU × N × f_E` ; énergie requête : `PUE × IT`
- GES usage : `énergie × 0,3844 kgCO2e/kWh` (mix USA)
- Fabrication : `latence / (3 ans × B) × [(GPU/8) × serveur + GPU × carte GPU]` avec serveur = 5 700 kgCO2e, 0,37 kgSb, 70 000 MJ ; GPU H100 = 273 kgCO2e, 0,00895 kgSb, 3 721 MJ
- Eau : `IT × (WUE_sur_site + PUE × 3,1321 L/kWh)` (l'eau des centrales électriques est incluse)

Hypothèses Anthropic : datacenters aux USA (AWS, Google), PUE 1,09–1,14, WUE sur site 0,13–0,999 L/kWh. Borne min = paramètres actifs, PUE et WUE minimaux ; borne max = maximaux.

## Paramètres des modèles (estimations EcoLogits, Anthropic ne publie rien)

| Modèle | Architecture | Total (Md) | Actifs (Md) | GPU |
|---|---|---|---|---|
| Fable 5 / 5.1 | MoE | 1 340 | 134–400 | 64 |
| Opus 4.5 → 5.5 | MoE | 670 | 67(70)–200 | 32 |
| Sonnet 4.5 / 4.6 | MoE | 440 | 44–132 | 16 |
| Sonnet 5 / 5.5 | MoE | 293 | 29–88 | 16 |
| Haiku 4.5 / 5.5 | dense | 10–35 | 10–35 | 1–2 |

Ordres de grandeur qui en découlent (pour 1 000 tokens générés) : Opus 5.5 ≈ 3 à 6 Wh ; Sonnet 5.5 ≈ 1 à 1,7 Wh ; Haiku 5.5 ≈ 0,06 à 0,15 Wh.

## Estimation complémentaire « contexte »

Hors EcoLogits, le script calcule aussi une estimation qui compte la lecture du contexte, avec les coefficients (approximatifs, de l'auteur) de S. P. Couch (2026) : 390 Wh/Mtok en entrée, 1 950 en sortie, 39 en lecture de cache, 490 en écriture de cache. Elle indique le poids possible du contexte en usage agentique ; ne pas la présenter comme une mesure.

## Limites à rappeler

- Paramètres et matériel d'Anthropic inconnus (TPU Google, Trainium AWS non modélisés) ; tout est extrapolé.
- Entraînement des modèles, réseau, stockage et terminal de l'utilisateur exclus.
- Mix électrique moyen des USA, pas celui des datacenters réels (Anthropic indique une part importante de gaz pour ses nouvelles capacités).
- Les mesures publiées par Google (0,24 Wh par requête médiane) sont 10 à 20 fois plus basses qu'EcoLogits pour une réponse courte : l'écart montre l'incertitude réelle.
