exec > /home/vboxuser/catty-reminders-app/deploy.log 2>&1
echo "=== Deploy started at $(date) ==="

cd /home/vboxuser/catty-reminders-app


git config --global --add safe.directory /home/vboxuser/catty-reminders-app

echo "Fetching origin..."
git fetch origin

echo "Resetting to origin/lab1..."
git reset --hard origin/lab1

echo "Pulling latest changes..."
git pull origin lab1

NEW_HEAD=$(git rev-parse HEAD)
echo "New HEAD is: $NEW_HEAD"

echo "DEPLOY_REF=$NEW_HEAD" > .env
echo "File .env updated."

./build.sh
./test.sh

sudo systemctl restart catty-app
echo "=== Deploy finished successfully ==="