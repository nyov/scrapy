import warnings
from scrapy.exceptions import ScrapyDeprecationWarning
warnings.warn("Module `scrapy.extensions.httpcache` is deprecated, "
              "use `scrapy_httpcache.httpcache` instead",
              ScrapyDeprecationWarning, stacklevel=2)

from scrapy_httpcache.httpcache import *
