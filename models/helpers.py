# -*- coding: utf-8 -*-

def svggauge(typeg,pct):
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
    return XML(response.render('svg/gauge.svg',color=color,symbol=XML(response.render('svg/gauge/%s.svg' % symbol, color=color)),pct=pct,transp=transp))

def svgicon(typeg):
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
    return XML(response.render('svg/gauge/%s.svg' % symbol, color=color))
