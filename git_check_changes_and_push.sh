#!/bin/bash

COMMIT_DATE=$(date -d "today" +"%Y-%m-%d-%H:%M")
GIT_REPO_URL=http://root:Pard@10./root/test.git
BRANCH_NAME=master

for dir in /data/opt/test
do
if [ ! -d "$dir" ]; then
break
fi
if [ ! -d "$dir/.git" ]
then
#перейти в рабочий каталог
    cd $dir/
#создать пустой Git репозиторий
    git init > /dev/null
#перейти в рабочий каталог
    cd $dir/
#добавить содержимое рабочего каталога в индекс
    git add .
#первый коммит
    git commit -m "$(echo -e $COMMIT_DATE: files add)" > /dev/null
#добавляем репозиторий и отправляем
    git remote add origin $GIT_REPO_URL > /dev/null
    git push -f origin $BRANCH_NAME > /dev/null
else
#перейти в рабочий каталог
    cd $dir/
#добавить содержимое рабочего каталога в индекс
    git add .
#отслеживаем изменения, разделяем их символом "|"
    git_changes=$(git status --porcelain $dir | sed 's/$/|/')
#коммитим изменения, отправить если есть изменения
    cd $dir/
#git status | grep modified > /dev/null
    git status | grep -E "(modified|deleted|new\ file)" > /dev/null
if [ $? -eq 0 ]
then
    git commit -m "$(echo -e $COMMIT_DATE: $git_changes)" > /dev/null
    git push -u origin $BRANCH_NAME
else
    echo "No changed files in $dir"
fi
#показать изменения
#git shortlog master
fi
done
