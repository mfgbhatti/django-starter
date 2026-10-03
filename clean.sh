#!/usr/bin/env bash
#
# Turn this starter into your own project.
#
# Asks for a project name, then rewrites every `django-starter` and
# `django_starter` (plus "Django Starter" in prose) to match, and renames
# src/django_starter/ to src/<your_module>/.
#
#   ./clean.sh                 # interactive
#   ./clean.sh "My Shop"       # name given, still asks the follow-up questions
#   ./clean.sh "My Shop" -y    # no questions: take the defaults
#
# "My Shop" becomes:  my-shop (pyproject, titles)  /  my_shop (Python package)

set -euo pipefail
cd "$(dirname "$0")"

OLD_SLUG="django-starter"
OLD_MODULE="django_starter"
OLD_TITLE="Django Starter"

NAME=""
YES=0
for arg in "$@"; do
    case "$arg" in
        -y|--yes) YES=1 ;;
        -h|--help) sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) NAME="$arg" ;;
    esac
done

die() { echo "error: $*" >&2; exit 1; }

# ask "question" default(Y|N) -> returns 0 for yes
ask() {
    local question="$1" default="$2" reply hint="[Y/n]"
    [ "$default" = "N" ] && hint="[y/N]"
    if [ "$YES" -eq 1 ]; then reply="$default"; else
        read -r -p "$question $hint " reply || reply=""
        reply="${reply:-$default}"
    fi
    case "$reply" in [Yy]*) return 0 ;; *) return 1 ;; esac
}

[ -d "src/$OLD_MODULE" ] || die "src/$OLD_MODULE not found - this project looks already cleaned."

if [ -z "$NAME" ]; then
    read -r -p "Project name (e.g. my-shop): " NAME
fi

# Normalise: lowercase, anything that isn't a letter/digit becomes a hyphen.
SLUG=$(printf '%s' "$NAME" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')
MODULE=${SLUG//-/_}
TITLE=$(printf '%s' "$SLUG" | tr '-' ' ' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1')

[[ "$SLUG" =~ ^[a-z][a-z0-9-]*$ ]] || die "the name must start with a letter and contain letters, digits or hyphens."
case "$MODULE" in
    django|accounts|manage|templates|sitestatic|assets|test|tests|site|config)
        die "'$MODULE' clashes with an existing Python/Django name - pick another." ;;
esac

echo
echo "  project name : $SLUG"
echo "  python module: $MODULE   (src/$MODULE/)"
echo "  display name : $TITLE"
echo
ask "Go ahead?" Y || { echo "Aborted."; exit 1; }

# 1. Rename the Django project package.
mv "src/$OLD_MODULE" "src/$MODULE"

# 2. Rewrite names inside text files (skips git, the venv, collectstatic output, binaries).
#    BSD and GNU sed both accept `-i.bak`.
FILES=$(grep -rIl -e "$OLD_SLUG" -e "$OLD_MODULE" -e "$OLD_TITLE" . \
    --exclude-dir=.git --exclude-dir=.venv --exclude-dir=assets \
    --exclude-dir=__pycache__ --exclude=clean.sh --exclude='*.sqlite3*' || true)
for f in $FILES; do
    sed -i.bak -e "s/$OLD_MODULE/$MODULE/g" -e "s/$OLD_SLUG/$SLUG/g" -e "s/$OLD_TITLE/$TITLE/g" "$f"
    rm -f "$f.bak"
done

# 3. A fresh project starts at a fresh version.
sed -i.bak -E 's/^version = ".*"/version = "0.1.0"/' pyproject.toml && rm -f pyproject.toml.bak
sed -i.bak -E '/^name = "'"$SLUG"'"$/{n;s/^version = ".*"/version = "0.1.0"/;}' uv.lock 2>/dev/null && rm -f uv.lock.bak

echo "Renamed $(printf '%s\n' $FILES | wc -l | tr -d ' ') files."

# 4. Local .env with a fresh secret key and DEBUG on.
if [ ! -f src/.env ] && ask "Create src/.env for local development?" Y; then
    KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
    sed -e "s/^DEBUG=.*/DEBUG=True/" -e "s|^SECRET_KEY=.*|SECRET_KEY=$KEY|" src/.env.dist > src/.env
    echo "Wrote src/.env"
fi

# 5. Refresh the lockfile if uv is around.
if command -v uv >/dev/null 2>&1; then
    uv lock >/dev/null 2>&1 && echo "Refreshed uv.lock" || echo "note: 'uv lock' failed - run it yourself."
fi

# 6. Optionally start a clean git history.
if [ -d .git ] && ask "Delete the starter's git history and start fresh?" N; then
    rm -rf .git
    git init -q -b main && echo "Initialised a new git repository."
fi

# 7. Remove this script - it has done its job.
if ask "Delete clean.sh?" Y; then
    rm -- "$0"
fi

cat <<DONE

Done. Next:
  uv sync
  uv run python src/manage.py migrate
  uv run python src/manage.py createsuperuser   # asks for email, username, password
  uv run python src/manage.py runserver
DONE
