# -*- coding: utf-8 -*-

def svggauge(typeg,pct,unit='%'):
    if typeg=='compfi':
        color = '#0cc3d6'
        symbol = 'compfi'
        transp = '0.24'
    elif typeg=='compem':
        color = '#ffc000'
        symbol ='compem'
        transp ='0.33'
    elif typeg=='diss':
        color = '#d6210c'
        symbol ='diss'
        transp ='0.23'
    elif typeg=="vote":
        color = "#999999"
        symbol ='vote'
        transp ='0.33'
    else:
        color = "#999999"
        symbol = typeg
        transp ='0.33'
    return XML(response.render('svg/gauge.svg',color=color,symbol=XML(response.render('svg/gauge/%s.svg' % symbol, color=color)),pct=pct,transp=transp,unit=unit))

def svgtop(typet):
    if typet=='top10':
        color = '#27bee0'
        colorlight = '#70cae8'
        label = 'TOP 10'
    elif typet=='top20':
        color = '#f9910b'
        colorlight = '#fcbd58'
        label = 'TOP 20'
    elif typet=='top50':
        color = '#f25a3c'
        colorlight = '#f57a3c'
        label = 'TOP 50'
    return XML(response.render('svg/part-top.svg', color=color, colorlight=colorlight, label=label))
