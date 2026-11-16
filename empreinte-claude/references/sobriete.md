# Leviers de sobriété avec Claude Code

Choisir 2 à 4 leviers selon ce que montrent les chiffres de la session. Chaque levier : quoi faire, pourquoi, effet attendu.

## 1. Choisir le modèle à la taille de la tâche (levier le plus fort)

- L'impact par token généré est à peu près proportionnel aux paramètres actifs (EcoLogits ; constat de l'ACV Mistral). Dans EcoLogits, 1 000 tokens coûtent ≈ 3–6 Wh avec Opus 5.5, ≈ 1–1,7 Wh avec Sonnet 5.5, ≈ 0,1 Wh avec Haiku 5.5.
- Pratique : `/model` pour passer à Sonnet ou Haiku sur les tâches courantes (renommage, petites corrections, résumés, recherche de fichiers) ; garder Opus ou Fable pour la conception, le débogage difficile, les gros raisonnements.
- Déclencheur : un modèle Opus ou Fable représente l'essentiel de l'énergie.

## 2. Doser l'effort de réflexion

- Les tokens de réflexion sont des tokens générés comme les autres. Avec le raisonnement activé, un même modèle peut consommer 150 à 700 fois plus (AI Energy Score v2, Hugging Face, 2025).
- Pratique : niveau d'effort bas ou moyen pour les tâches simples ; réserver l'effort élevé aux problèmes qui le justifient.
- Déclencheur : la réflexion dépasse ≈ 30 % des tokens générés.

## 3. Maîtriser le contexte

- Chaque requête relit tout le contexte ; avec 100 k tokens d'entrée, une requête peut coûter ≈ 100 fois plus qu'une question courte (Epoch AI). Le cache réduit fortement ce coût sans l'annuler.
- Pratique : `/clear` entre deux tâches sans lien ; `/compact` dans les longues sessions ; pointer vers les lignes utiles plutôt que faire lire des fichiers entiers ; éviter de coller de gros journaux.
- Déclencheur : contexte relu de plusieurs millions de tokens, ou estimation complémentaire « contexte » bien supérieure à l'estimation EcoLogits.

## 4. Déléguer avec discernement

- Chaque sous-agent repart d'un contexte neuf et génère ses propres tokens ; plusieurs en parallèle multiplient la consommation.
- Pratique : déléguer ce qui est vraiment parallèle ou volumineux ; faire soi-même les recherches ciblées ; préciser un modèle léger pour les sous-agents de recherche.
- Déclencheur : les sous-agents génèrent une part importante des tokens.

## 5. Ne pas refaire ce qui existe

- Une réponse réutilisée ne coûte rien. Pratique : transformer les demandes récurrentes en skills, scripts ou modèles ; regrouper plusieurs petites questions en une demande claire ; formuler précisément pour éviter les allers-retours.
- Déclencheur : beaucoup de sessions courtes et répétitives sur une période.

## 6. Se demander si l'IA est utile

- Une recherche dans la documentation, un `grep` ou une calculatrice suffisent souvent ; un modèle généraliste consomme beaucoup plus qu'un outil spécialisé pour la même tâche (Luccioni et al., 2024).

## Ton

Pas de culpabilisation : l'impact d'une session reste modeste face à un trajet en voiture ou un repas carné. Pas de minimisation non plus : à l'échelle d'une équipe et d'une année, ces consommations s'additionnent, et la demande en électricité des datacenters double d'ici 2030 (AIE). Le message utile : « voici ce qui pèse le plus dans votre usage, et ce qui le réduit le plus facilement ».
