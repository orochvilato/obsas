# -*- coding: utf-8 -*-
# essayez quelque chose comme
def index():
    import tools
    from sources.hatvp import declarations
    from sources.deputywatch import deputywatch
    from sources.acteurs_organes import andata
    from sources.scrutins import getScrutins
    
    return dict(d=len(declarations),e=len(deputywatch),a=andata.keys(),s=getScrutins().keys())
