max_page=$1
if [ ! "$1" ];then
    max_page=5
fi
echo "max_page=${max_page}"
scrapy crawl hupu_post -a max_page=${max_page}
echo "end scrawl..."