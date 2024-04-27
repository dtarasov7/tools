#!/bin/bash

COMMIT_DATE=$(date -d "today" +"%Y-%m-%d-%H:%M")

for dir in /path/first /path/second
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
else
#перейти в рабочий каталог
        cd $dir/
#добавить содержимое рабочего каталога в индекс
        git add .
#отслеживаем изменения, разделяем их символом "|"
        git_changes=$(git status --porcelain $dir | sed 's/$/|/')
#коммитим изменения
        git commit -m "$(echo -e $COMMIT_DATE: $git_changes)" > /dev/null
#показать изменения
#git shortlog master
fi
done

