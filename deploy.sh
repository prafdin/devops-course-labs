cd /home/vboxuser/catty-reminders-app


git fetch origin
git reset --hard origin/lab1


git pull origin lab1


echo "DEPLOY_REF=$(git rev-parse HEAD)" > .env


./build.sh
./test.sh


sudo systemctl restart catty-app