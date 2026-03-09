set -e

REPO_DIR="/mnt/c/Users/Sergo/Documents/prog/university/catty-reminders-app"
BRANCH=$1

cd "$REPO_DIR"

git fetch origin
git checkout -B "$BRANCH" "origin/$BRANCH"
echo "Pull origin $BRANCH"
git pull origin "$BRANCH"

echo "Running tests"

if [ ! -d ".venv" ]; then
	echo "Virual environment was not found, creating..."
	python3 -m venv .venv/
fi

source .venv/bin/activate
echo "Virtual environment activated"

if [ -f "requirements.txt" ]; then
	echo ">Installing/Updating requirements"
	pip install -r requirements.txt
fi

echo "Running pytest"
python3 -m pytest -v

echo "Tests finished"