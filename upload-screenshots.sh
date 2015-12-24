set -e
wget -q http://imgur.com/tools/imgurbash.sh
chmod +x ./imgurbash.sh
for i in screenshots/*.png
do
    echo "### $i"|tee -a results.md
    echo >> results.md
    URL="$(./imgurbash.sh $i 2>/dev/null)"
    echo "![$i]($URL)"|tee -a results.md
done
wget http://wgetpaste.zlin.dk/wgetpaste-current.tar.bz2
tar xf wgetpaste-current.tar.bz2
chmod +x wgetpaste-*/wgetpaste
cat << END

SCREENSHOTS OF THIS TESTSUITE:
END
cat results.md | wgetpaste-*/wgetpaste -l Markdown -s gists
