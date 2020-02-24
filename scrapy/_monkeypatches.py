import copyreg

try:
    """ HACK to use python builtin idna lookup for emoji TLD domain names """
    import idna
    from idna import encode as iencode, decode as idecode
    # ccTLD list generated from:
    # scrapy shell 'https://emojicatch.com/%F0%9F%98%80'
    # >>> tlds = tuple(response.xpath('//div[@id="results"]/button/p/text()').getall())
    tlds = ('.ws', '.to', '.ga', '.cf', '.tk', '.ml', '.gq', '.st', '.fm', '.je', '.gg', '.radio.am', '.radio.fm', '.kz', '.com.kz', '.org.kz')
    tldb = tuple([t.encode() for t in tlds])
    idna.encode = lambda text: text.encode("idna") if text.endswith(tlds) else iencode(text)
    idna.decode = lambda octs: octs.decode("idna") if octs.endswith(tldb) else idecode(octs)
except: pass

# Undo what Twisted's perspective broker adds to pickle register
# to prevent bugs like Twisted#7989 while serializing requests
import twisted.persisted.styles  # NOQA
# Remove only entries with twisted serializers for non-twisted types.
for k, v in frozenset(copyreg.dispatch_table.items()):
    if not str(getattr(k, '__module__', '')).startswith('twisted') \
            and str(getattr(v, '__module__', '')).startswith('twisted'):
        copyreg.dispatch_table.pop(k)
