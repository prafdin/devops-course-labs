BRANCH=${1:-lab1}

exec > /home/vboxuser/catty-reminders-app/deploy.log 2>&1
echo "=== Deploy started at $(date) for branch $BRANCH ==="

cd /home/vboxuser/catty-reminders-app
git config --global --add safe.directory /home/vboxuser/catty-reminders-app

git fetch origin

git checkout $BRANCH
git reset --hard origin/$BRANCH
git pull origin $BRANCH

NEW_HEAD=$(git rev-parse HEAD)
echo "DEPLOY_REF=$NEW_HEAD" > .env

./build.sh
./test.sh

sudo systemctl restart catty-app
echo "=== Deploy finished successfully ==="