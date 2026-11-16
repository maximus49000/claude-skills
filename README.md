# claude-skills

Skills Claude Code partagées. Chaque dossier est une skill autonome.

## empreinte-claude

Estime l'impact environnemental (énergie, CO2e, eau, métaux) de ton usage de Claude Code à partir des tokens réellement consommés, selon la méthodologie [EcoLogits](https://ecologits.ai/latest/methodology/llm_inference/), et propose des conseils de sobriété adaptés.

### Installer

Prérequis : Claude Code (CLI ou onglet Code de l'application de bureau) et Python 3 dans le PATH. Le script n'utilise que la bibliothèque standard.

**Option 1 – pour tous tes projets (recommandé)** : cloner le dépôt, puis lier le dossier de la skill dans tes skills personnelles. Un `git pull` suffit ensuite pour la mettre à jour.

Windows (invite de commandes `cmd`) :

```bat
git clone https://github.com/maximus49000/claude-skills.git "%USERPROFILE%\Documents\claude-skills"
mkdir "%USERPROFILE%\.claude\skills" 2>nul
mklink /J "%USERPROFILE%\.claude\skills\empreinte-claude" "%USERPROFILE%\Documents\claude-skills\empreinte-claude"
```

macOS / Linux :

```bash
git clone https://github.com/maximus49000/claude-skills.git ~/Documents/claude-skills
mkdir -p ~/.claude/skills
ln -s ~/Documents/claude-skills/empreinte-claude ~/.claude/skills/empreinte-claude
```

Mettre à jour :

```bash
git -C ~/Documents/claude-skills pull
```

Sans git : télécharger le ZIP du dépôt (bouton « Code » → « Download ZIP » sur GitHub) et copier le dossier `empreinte-claude` dans `~/.claude/skills/`. Il faudra le recopier à chaque mise à jour.

Tu peux aussi demander directement à Claude Code : « installe la skill empreinte-claude depuis https://github.com/maximus49000/claude-skills ».

**Option 2 – pour un seul projet** : copier `empreinte-claude/` dans `<projet>/.claude/skills/` et le commiter avec le projet. La skill est alors partagée avec tous ceux qui travaillent sur ce dépôt.

**Option 3 – fichier `.skill`** : installer `empreinte-claude.skill` depuis les réglages de Claude (Capacités → Skills). La skill ne sert que dans Claude Code, car elle lit les transcripts locaux.

Ouvre ensuite une nouvelle session Claude Code : la skill apparaît dans la liste des skills disponibles.

### Vérifier l'installation

Dans une **nouvelle** session Claude Code (les skills sont chargées au démarrage), tape `/` dans la zone de message : `empreinte-claude` doit apparaître dans la liste. Sinon, vérifie que le dossier `%USERPROFILE%\.claude\skills\empreinte-claude` existe (Windows) ou `~/.claude/skills/empreinte-claude` (macOS / Linux), puis ouvre une nouvelle session.

### Utiliser

La skill ne fonctionne que dans Claude Code (terminal ou onglet Code de l'application de bureau) : elle lit les historiques de conversation enregistrés sur le poste. Dans une conversation claude.ai classique, ces données n'existent pas.

**1. Avec la commande (le plus fiable)** : taper `/empreinte-claude`, éventuellement suivi de la demande.

- `/empreinte-claude` : bilan de la session en cours
- `/empreinte-claude depuis le 1er novembre, tous projets`
- `/empreinte-claude rapport HTML du mois`

**2. En langage naturel** : Claude charge la skill tout seul quand la demande correspond à sa description.

- « Quel est l'impact écologique de cette session ? »
- « Fais-moi le bilan carbone de mon usage de Claude Code depuis le 1er novembre, tous projets confondus. »
- « Est-ce que passer de Opus à Haiku change vraiment quelque chose ? »
- « Comment utiliser Claude de façon plus sobre ? »
- « Fais-moi un rapport HTML de mon empreinte du mois. »

Avec une question courte ou vague, Claude peut répondre de lui-même sans charger la skill : utiliser alors la commande.

Claude lance le script, présente une fourchette (min–max) avec des équivalences, explique d'où vient l'impact (modèle, réflexion, sous-agents, contexte) et propose 2 à 4 leviers concrets.

Le script s'utilise aussi seul :

```bash
python empreinte-claude/scripts/empreinte.py                                   # session la plus récente du dossier courant
python empreinte-claude/scripts/empreinte.py --since 2026-11-01                # sessions du projet depuis une date
python empreinte-claude/scripts/empreinte.py --all-projects --since 2026-11-01 # tout l'usage depuis une date
python empreinte-claude/scripts/empreinte.py --session <id> --json             # une session, en JSON
```

Sous Windows, si les accents s'affichent mal : `set PYTHONIOENCODING=utf-8` avant de lancer le script.

### Limites

Ce sont des estimations, pas des mesures. Anthropic ne publie aucun chiffre par requête : les paramètres des modèles sont estimés par EcoLogits, et EcoLogits ne compte que les tokens générés, sans la relecture du contexte. Le script ajoute donc une estimation complémentaire, indicative, qui en tient compte. Le détail est dans `empreinte-claude/references/`.

### Mettre à jour les données

`empreinte-claude/scripts/ecologits_data.json` reprend les constantes et les modèles d'EcoLogits v0.11.3 (relevés le 16/11/2026). Pour un nouveau modèle Claude, ajoute son entrée à partir du fichier `models.json` d'EcoLogits (lien dans le fichier). En attendant, un modèle inconnu est approximé par sa famille.

### Tests

`empreinte-claude/evals/` contient 3 cas de test, lisibles par `claude plugin eval`.
