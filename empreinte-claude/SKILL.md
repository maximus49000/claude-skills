---
name: empreinte-claude
description: Estime et explique l'impact environnemental (énergie, CO2e, eau, métaux) de l'utilisation de Claude dans Claude Code, à partir des tokens réellement consommés par la session, le projet ou une période, selon la méthodologie EcoLogits, puis donne des conseils de sobriété personnalisés. À utiliser dès que l'utilisateur demande « quel est mon impact », « combien de CO2 / d'énergie / d'eau a consommé cette session », « mon empreinte carbone avec Claude », « bilan écologique », « est-ce que Claude pollue », « comment utiliser Claude de façon plus sobre / frugale », ou veut un rapport d'empreinte numérique de son usage de l'IA, même s'il ne cite pas EcoLogits.
---

# Empreinte environnementale de Claude (Claude Code)

But : rendre visible, sans culpabiliser ni minimiser, ce que coûte à la planète l'usage de Claude, puis donner 2 à 4 leviers concrets adaptés à l'usage observé. La personne doit repartir avec un ordre de grandeur juste, une idée claire de l'incertitude, et une chose à faire différemment.

## 1. Mesurer

Lancer le script (Python 3, bibliothèque standard seulement) depuis le dossier du projet :

```bash
python <dossier-de-la-skill>/scripts/empreinte.py            # session en cours (la plus récente du projet)
python <dossier-de-la-skill>/scripts/empreinte.py --since 2026-11-01                 # toutes les sessions du projet depuis une date
python <dossier-de-la-skill>/scripts/empreinte.py --all-projects --since 2026-11-01  # tout l'usage Claude Code depuis une date
python <dossier-de-la-skill>/scripts/empreinte.py --session <id> --json              # session précise, sortie JSON
```

Sous Windows, préfixer par `PYTHONIOENCODING=utf-8` si les accents s'affichent mal. Si l'utilisateur parle de « cette conversation », prendre la session courante ; « ce mois-ci », « depuis lundi » → `--since` ; « tout mon usage » → `--all-projects --since`. Si le périmètre est flou, prendre la session courante et proposer l'élargissement en une phrase.

Le script lit les transcripts locaux `~/.claude/projects/…/*.jsonl` (y compris les sous-agents), compte les tokens par requête API et applique EcoLogits (détail : `references/methodologie.md`). Il sort une fourchette min–max, le détail par modèle, des équivalences et une estimation complémentaire tenant compte du contexte relu.

## 2. Restituer le bilan (par défaut : texte court en chat)

Structure recommandée, en français :

1. **Une phrase-clé** avec l'ordre de grandeur le plus parlant (souvent l'énergie et le CO2e, avec une équivalence).
2. **Le tableau** fourchette min–max (énergie, GES dont fabrication, eau, métaux). Garder les fourchettes : afficher un chiffre unique laisserait croire à une précision qui n'existe pas.
3. **D'où vient l'impact** : modèle dominant, part des tokens de réflexion (thinking), part des sous-agents. C'est ce qui rend les conseils pertinents.
4. **Le poids du contexte relu**, en paragraphe à part (section « Poids du contexte relu » du script). En usage agentique, chaque requête relit toute la conversation, les fichiers lus et les sorties d'outils : souvent plus de 100 000 tokens par requête. EcoLogits l'ignore ; l'estimation complémentaire, indicative, peut être plusieurs fois supérieure. Présenter les deux lectures côte à côte (« génération seule, méthode EcoLogits » et « relecture du contexte comprise, ordre de grandeur ») plutôt que d'en cacher une : la première est la plus sourcée, la seconde montre souvent le principal levier d'action. Quand le rapport dépasse ×2 ou que le contexte moyen dépasse 100 000 tokens, le dire clairement et faire du contexte un des premiers leviers.
5. **Fiabilité** en 2-3 lignes : Anthropic ne publie aucun chiffre par requête ; les paramètres des modèles sont estimés par EcoLogits ; les coefficients de l'estimation « contexte » sont grossiers. Les mesures publiées par Google (0,24 Wh par requête Gemini médiane) sont nettement plus basses qu'EcoLogits : citer les deux montre l'état réel des connaissances.
6. **2 à 4 leviers de sobriété** choisis selon les données (voir section 3), chacun avec son effet attendu.
7. Proposer en une ligne le rapport HTML.

Équivalences : en choisir deux ou trois parlantes, pas toutes. Pour l'énergie, privilégier le vélo (heures de pédalage sur un vélo générateur à ~100 W, ou km de vélo) : rendre l'énergie en effort physique la rend concrète, par exemple « il faudrait pédaler 6 h pour produire l'électricité de cette session ». Pour donner du recul, comparer aussi à un geste courant (un repas végétarien ≈ 850 g CO2e, ADEME) : une session typique pèse bien moins qu'un trajet en voiture, mais un usage intensif quotidien s'additionne. L'objectif est la juste proportion, ni alarmisme ni « c'est négligeable ».

Pour les sources et chiffres de comparaison : `references/sources.md`.

## 3. Conseils de sobriété personnalisés

Lire `references/sobriete.md` et retenir les leviers qui correspondent à ce que montrent les données, par exemple :

- Modèle le plus gros (Opus, Fable) majoritaire → réserver ce modèle aux tâches difficiles, Sonnet ou Haiku pour le reste (impact ≈ proportionnel aux paramètres actifs : Haiku ≈ 40 fois moins qu'Opus, Sonnet ≈ 3 fois moins dans EcoLogits).
- Part de réflexion élevée (> 30 % des tokens générés) → baisser le niveau d'effort pour les tâches simples.
- Sous-agents nombreux → ne déléguer que ce qui le justifie.
- Contexte moyen > 100 000 tokens ou estimation « contexte » > 2× EcoLogits → `/clear` entre deux tâches sans lien, `/compact`, éviter de charger des fichiers entiers inutilement.
- Nombreuses sessions courtes répétitives → regrouper les demandes, réutiliser des skills et scripts plutôt que régénérer.

Toujours formuler les conseils comme des options concrètes, pas comme des reproches.

## 4. Rapport HTML (sur demande)

Si l'utilisateur veut un rapport : relancer le script avec `--json`, puis produire une page HTML autonome (graphiques simples : répartition par modèle, fourchettes, équivalences ; section hypothèses et sources). Si une skill de charte graphique est disponible (par exemple `charte-operis`), la charger avant d'écrire la page et l'appliquer. Toujours inclure la date, le périmètre (session, période), la version d'EcoLogits et la mention « estimation, pas une mesure ».

## Si le script ne trouve rien

- Pas de transcript : la skill fonctionne seulement dans Claude Code (les transcripts sont locaux). Expliquer et proposer une estimation à la main à partir d'un nombre de tokens donné, avec les ordres de grandeur de `references/methodologie.md`.
- Modèle inconnu : le script l'approxime par sa famille et l'indique ; le signaler dans le bilan.
- Données EcoLogits anciennes : `scripts/ecologits_data.json` indique sa date et comment le mettre à jour.
