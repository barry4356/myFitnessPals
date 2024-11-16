python --version
which python
python ./mfp_scrape.py
cp temp.md Reports/README.md
mdy=`date +%m-%d-%Y`
echo $mdy
cp temp.md Reports/Reports/${mdy}_report.md
pushd Reports
commit_message="${mdy}: Ran Report"
echo $commit_message
git pull
git add Reports/*.md
git add *.md
git commit -m "${commit_message}" && git push
popd
