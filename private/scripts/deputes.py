#!/home/www-data/web2py/applications/obsas/.pyenv/bin/python
# -*- coding: utf-8 -*-

import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')

import scrapy
import requests
import json
import re

dep_template = {
    "adresses": [
        {
            "adresseDeRattachement": null,
            "codePostal": "75355",
            "complementAdresse": null,
            "intitule": "Assembl\u00e9e nationale,",
            "nomRue": "Rue de l'Universit\u00e9,",
            "numeroRue": "126",
            "poids": "01",
            "type": "AdressePostale_Type",
            "typeLibelle": "Adresse officielle",
            "uid": "AD718938",
            "ville": "Paris 07 SP"
        },
        {
            "adresseDeRattachement": null,
            "poids": null,
            "type": "AdresseSiteWeb_Type",
            "typeLibelle": "Twitter",
            "uid": "AD725764",
            "valElec": "@jlmelenchon"
        },
        {
            "adresseDeRattachement": null,
            "poids": null,
            "type": "AdresseSiteWeb_Type",
            "typeLibelle": "Facebook",
            "uid": "AD726080",
            "valElec": "jlmelenchon"
        },
        {
            "adresseDeRattachement": null,
            "poids": null,
            "type": "AdresseSiteWeb_Type",
            "typeLibelle": "Site internet",
            "uid": "AD726222",
            "valElec": "www.melenchon.fr"
        },
        {
            "adresseDeRattachement": null,
            "poids": null,
            "type": "AdresseMail_Type",
            "typeLibelle": "M\u00e8l",
            "uid": "AD727917",
            "valElec": "jean-luc.melenchon@assemblee-nationale.fr"
        }
    ],
    "age": 65,
    "circo": "4",
    "classeage": "60-70 ans",
    "commissions": [
        "PO59047",
        "PO725343"
    ],
    "contacts": [
        [
            "Twitter",
            "@jlmelenchon"
        ],
        [
            "Facebook",
            "jlmelenchon"
        ],
        [
            "Site internet",
            "www.melenchon.fr"
        ],
        [
            "M\u00e8l",
            "jean-luc.melenchon@assemblee-nationale.fr"
        ]
    ],
    "csp": "Cadres et professions intellectuelles sup\u00e9rieures",
    "departement": "Bouches-du-Rh\u00f4ne",
    "deputywatch": null,
    "etatCivil_dateDeces": null,
    "etatCivil_ident_alpha": "Melenchon",
    "etatCivil_ident_civ": "M.",
    "etatCivil_ident_nom": "M\u00e9lenchon",
    "etatCivil_ident_prenom": "Jean-Luc",
    "etatCivil_infoNaissance_dateNais": "1951-08-19",
    "etatCivil_infoNaissance_depNais": null,
    "etatCivil_infoNaissance_paysNais": "Maroc",
    "etatCivil_infoNaissance_villeNais": "Tanger",
    "fonctions": [
        {
            "debut": "18 juin 2017",
            "organe": "PO717460",
            "organe_libelle": "de l'Assembl\u00e9e",
            "qualite": "membre"
        },
        {
            "debut": "27 juin 2017",
            "organe": "PO730958",
            "organe_libelle": "du groupe La France insoumise",
            "qualite": "Pr\u00e9sident"
        },
        {
            "debut": "29 juin 2017",
            "organe": "PO59047",
            "organe_libelle": "de la commission des affaires \u00e9trang\u00e8res",
            "qualite": "Membre"
        },
        {
            "debut": "27 juin 2017",
            "organe": "PO725343",
            "organe_libelle": "de la Conf\u00e9rence des Pr\u00e9sidents",
            "qualite": "Membre"
        }
    ],
    "groupe": "PO730958",
    "groupe_abrev": "FI",
    "groupe_nom": "La France insoumise",
    "hatvp": [],
    "id": "m.jeanlucmelenchon",
    "idcirco": "013-04",
    "iddepartement": "013",
    "interventions": 311,
    "mandats": [
        {
            "InfosHorsSIAN_HATVP_URI": null,
            "acteurRef": "PA2150",
            "collaborateurs": [
                {
                    "@xsi:nil": "true"
                },
                {
                    "@xsi:nil": "true"
                }
            ],
            "dateDebut": "2017-06-18",
            "dateFin": null,
            "datePublication": null,
            "election_causeMandat": "\u00e9lections g\u00e9n\u00e9rales",
            "election_lieu_departement": "Bouches-du-Rh\u00f4ne",
            "election_lieu_numCirco": "4",
            "election_lieu_numDepartement": "13",
            "election_lieu_region": "Provence-Alpes-C\u00f4te d'Azur",
            "election_lieu_regionType": "M\u00e9tropolitain",
            "infosQualite_codeQualite": "membre",
            "infosQualite_libQualite": "membre",
            "infosQualite_libQualiteSex": "membre",
            "legislature": "15",
            "mandature_causeFin": null,
            "mandature_datePriseFonction": "2017-06-21",
            "mandature_mandatRemplaceRef": null,
            "mandature_placeHemicycle": "601",
            "mandature_premiereElection": "0",
            "nominPrincipale": "1",
            "organes_organeRef": "PO717460",
            "preseance": "50",
            "suppleants_suppleant_dateDebut": "2017-06-18",
            "suppleants_suppleant_dateFin": null,
            "suppleants_suppleant_suppleantRef": "PA718940",
            "type": "MandatParlementaire_type",
            "typeOrgane": "ASSEMBLEE",
            "uid": "PM722506"
        },
        {
            "acteurRef": "PA2150",
            "dateDebut": "2017-06-27",
            "dateFin": null,
            "datePublication": "2017-06-28",
            "infosQualite_codeQualite": "Membre",
            "infosQualite_libQualite": "Membre du",
            "infosQualite_libQualiteSex": "Membre du",
            "legislature": "15",
            "nominPrincipale": "0",
            "organes_organeRef": "PO730958",
            "preseance": "20",
            "type": "MandatSimple_Type",
            "typeOrgane": "GP",
            "uid": "PM731514"
        },
        {
            "acteurRef": "PA2150",
            "dateDebut": "2017-06-27",
            "dateFin": null,
            "datePublication": "2017-06-28",
            "infosQualite_codeQualite": "Pr\u00e9sident",
            "infosQualite_libQualite": "Pr\u00e9sident du",
            "infosQualite_libQualiteSex": "Pr\u00e9sident du",
            "legislature": "15",
            "nominPrincipale": "1",
            "organes_organeRef": "PO730958",
            "preseance": "1",
            "type": "MandatSimple_Type",
            "typeOrgane": "GP",
            "uid": "PM731529"
        },
        {
            "InfosHorsSIAN_HATVP_URI": null,
            "acteurRef": "PA2150",
            "collaborateurs": null,
            "dateDebut": "2017-06-27",
            "dateFin": null,
            "datePublication": "2017-06-28",
            "election_causeMandat": null,
            "election_lieu_departement": null,
            "election_lieu_numCirco": null,
            "election_lieu_numDepartement": null,
            "election_lieu_region": null,
            "election_lieu_regionType": null,
            "infosQualite_codeQualite": "Membre",
            "infosQualite_libQualite": "Membre",
            "infosQualite_libQualiteSex": "Membre",
            "legislature": "15",
            "mandature_causeFin": null,
            "mandature_datePriseFonction": null,
            "mandature_mandatRemplaceRef": null,
            "mandature_placeHemicycle": null,
            "mandature_premiereElection": null,
            "nominPrincipale": "1",
            "organes_organeRef": "PO725343",
            "preseance": "20",
            "suppleants": null,
            "type": "MandatParlementaire_type",
            "typeOrgane": "CONFPT",
            "uid": "PM731530"
        },
        {
            "acteurRef": "PA2150",
            "dateDebut": "2017-06-29",
            "dateFin": null,
            "datePublication": "2017-06-29",
            "infosQualite_codeQualite": "Membre",
            "infosQualite_libQualite": "Membre",
            "infosQualite_libQualiteSex": "Membre",
            "legislature": "15",
            "nominPrincipale": "1",
            "organes_organeRef": "PO59047",
            "preseance": "32",
            "type": "MandatSimple_Type",
            "typeOrgane": "COMPER",
            "uid": "PM731654"
        }
    ],
    "nomcomplet": "M. Jean-Luc M\u00e9lenchon",
    "nomprenom": "M\u00c9LENCHON Jean-Luc",
    "organes": [
        "AN",
        "FI",
        "CION_AFETR",
        "CNFPDT"
    ],
    "place": "601",
    "prenomnom": "Jean-Luc M\u00c9LENCHON",
    "profession_libelleCourant": "Professeur",
    "profession_socProcINSEE_catSocPro": "Cadres de la fonction publique, professions intellectuelles et  artistiques",
    "profession_socProcINSEE_famSocPro": "Cadres et professions intellectuelles sup\u00e9rieures",
    "region": "Provence-Alpes-C\u00f4te d'Azur",
    "sexe": "Homme",
    "typeregion": "M\u00e9tropolitain",
    "uid": "PA2150",
    "uid_type": "IdActeur_type"
}



from scrapy.crawler import CrawlerProcess

import unicodedata
def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')
def normalize(s):
    return strip_accents(s).encode('utf8').replace(' ','').replace('-','').replace('\x0a','').replace('\xc5\x93','oe').lower() if s else s

deputes = []
class DeputesSpider(scrapy.Spider):
    name = "deputes"
    base_url = 'http://www2.assemblee-nationale.fr'
    def start_requests(self):
        request = scrapy.Request(url=self.base_url+'/deputes/liste/tableau', callback=self.parse_listedeputes)
        yield request



    def parse_listedeputes(self, response):
        for dep in response.xpath('//table[@class="deputes"]/tbody/tr'):
            depitems = dep.xpath('./td')
            depurl = depitems[0].xpath('a/@href').extract()[0]
            depdept = depitems[1].xpath('text()').extract()[0]
            depcirc = depitems[2].xpath('text()').extract()[0]
            request = scrapy.Request(url=self.base_url + depurl, callback=self.parse_depute, dont_filter=True)
            request.meta['dep'] = depdept
            request.meta['circ'] = depcirc
            yield request


    def parse_depute(self, response):
        nom = response.xpath('//div[contains(@class,"titre-bandeau-bleu")]/h1/text()').extract()[0]
        uid = response.url.split('_')[1]
        departement = response.meta['dep']
        circo = response.meta['dep']
        suppleant = response.xpath('//dt[text()[contains(.," Suppl")]]/following-sibling::dd/ul/li/text()')
        suppleant = suppleant[0].extract() if suppleant else None
        nais = response.xpath('//dt[text()[contains(.,"Biog")]]/following-sibling::dd/ul/li/text()')[0].extract()
        nais = re.search(r'le ([0-9]+.+[0-9]+) . ([^)]+\))',nais).groups()
        ddn = datetime.datetime.strptime(nais[0],'%d %B %Y')
        nais_lieu = nais[1]
        deputes.append(dict(
            nom = nom,
            uid = uid,
            departement = departement,
            circo = circo,
            suppleant = suppleant,
            ddn = ddn,
            nais_lieu = nais_lieu
            ))

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)','DOWNLOAD_DELAY':0.25
})


process.crawl(DeputesSpider)
process.start() # the script will block here until the crawling is finished

print deputes
exit()
import json
with open('/tmp/scrutins.json','w') as f:
    f.write(json.dumps(scrutins))
