"""Loob data/taimed.xlsx Claude'i tabeli „Taimed“ sisust (19.11.2026)."""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

COLS = ["Taim", "Ladinakeelne nimi", "Tüüp", "Istutusvahe (m)", "Hekis (tk/jm)", "Müügivorm", "Hind (€/tk)",
        "Kõrgus (m)", "Laius (m)", "Valgus", "Õitseb", "Õis / dekoratiivsus", "Märkused", "Pärismaine",
        "Kuju (valikuline)", "Õievärv hex (valikuline)"]
N = None
R = [
("Väikeselehine pärn","Tilia cordata","Lehtpuu",8,N,"16–18 cm ümbermõõt",20,12,"Päike–poolvari","juuli","kollakasvalge, lõhnav","Allee- ja tänavapuu","Jah"),
("Harilik vaher","Acer platanoides","Lehtpuu",10,N,"16–18 cm ümbermõõt",20,15,"Päike–poolvari","mai","kollakasroheline","Kollane-oranž sügisvärv","Jah"),
("Harilik vaher 'Globosum'","Acer platanoides 'Globosum'","Lehtpuu",5,N,"14–16 cm, tüvi 2 m",5,5,"Päike–poolvari","mai","kerajas võra","Kitsastesse kohtadesse, tänavale","Pärismaise liigi sort"),
("Arukask","Betula pendula","Lehtpuu",6,N,"14–16 cm ümbermõõt",20,8,"Päike","aprill–mai","valge koor",N,"Jah"),
("Harilik pihlakas","Sorbus aucuparia","Lehtpuu",5,N,"12–14 cm ümbermõõt",10,5,"Päike–poolvari","mai–juuni","valge; punased viljad",N,"Jah"),
("Iluõunapuu","Malus (ilusordid)","Lehtpuu",4,N,"10–12 cm ümbermõõt",5,4,"Päike","mai","roosa / punane / valge","Väikesed dekoratiivsed viljad","Ei"),
("Harilik tamm","Quercus robur","Lehtpuu",12,N,"16–18 cm ümbermõõt",25,20,"Päike","mai",N,"Pikaealine, vajab ruumi","Jah"),
("Harilik valgepöök","Carpinus betulus","Lehtpuu",6,4,"80–100 cm, paljasjuurne (hekk)",15,8,"Päike–poolvari",N,"kuivad lehed püsivad talvel","Pügatav hekk","Ei"),
("Harilik mänd","Pinus sylvestris","Okaspuu",6,N,"150–200 cm, potis",20,8,"Päike",N,N,"Kuivad liivased mullad","Jah"),
("Harilik kuusk","Picea abies","Okaspuu",5,2.5,"100–125 cm",25,6,"Päike–vari",N,N,"Hekiks pügatult","Jah"),
("Harilik elupuu 'Brabant'","Thuja occidentalis 'Brabant'","Okaspuu",2,2,"100–125 cm, C10",10,3,"Päike–poolvari",N,N,"Kiirekasvuline hekk","Ei"),
("Harilik elupuu 'Smaragd'","Thuja occidentalis 'Smaragd'","Okaspuu",1,2.5,"80–100 cm, C5",4,1.2,"Päike–poolvari",N,"kitsas koonus","Levinuim hekitaim","Ei"),
("Harilik elupuu 'Danica'","Thuja occidentalis 'Danica'","Igihaljas põõsas",0.6,N,"30–40 cm, C3",0.6,0.8,"Päike–poolvari",N,"kerajas","Madal ääris","Ei"),
("Kanada kuusk 'Conica'","Picea glauca 'Conica'","Igihaljas põõsas",1.5,N,"40–60 cm, C5",2.5,1.5,"Päike–poolvari",N,"tihe koonus","Aeglane kasv; kevadine põletusoht","Ei"),
("Mägimänd","Pinus mugo","Igihaljas põõsas",1.5,N,"30–40 cm, C5",1.5,2,"Päike",N,N,"Kõrgus sõltub sordist","Ei"),
("Horisontaalne kadakas","Juniperus horizontalis","Igihaljas põõsas",1.2,N,"30–40 cm, C3",0.3,2,"Päike",N,"roomav","Pinnakattev","Ei"),
("Kasakakadakas","Juniperus sabina","Igihaljas põõsas",1.2,N,"30–40 cm, C3",1,2.5,"Päike",N,"laiuv","Nõlvadele","Ei"),
("Keskmine marjakuusk 'Hicksii'","Taxus × media 'Hicksii'","Igihaljas põõsas",1.2,3,"60–80 cm, C5",3,1.5,"Poolvari–vari",N,N,"Mürgine; varjutaluv hekk","Ei"),
("Rododendron (hübriidid)","Rhododendron","Igihaljas põõsas",1,N,"30–40 cm, C5",1.5,1.5,"Poolvari","mai–juuni","mitmesugune","Happeline turbamuld","Ei"),
("Harilik sirel","Syringa vulgaris","Lehtpõõsas",2,2,"60–80 cm, C5",4,3,"Päike","mai–juuni","lilla / valge, lõhnav","Annab juurevõsusid","Ei"),
("Aed-ebajasmiin","Philadelphus coronarius","Lehtpõõsas",1.5,2,"60–80 cm, C3",2.5,2,"Päike–poolvari","juuni–juuli","valge, lõhnav",N,"Ei"),
("Lodjapuulehine põisenelas","Physocarpus opulifolius","Lehtpõõsas",1.2,2.5,"40–60 cm, C3",2.5,2,"Päike–poolvari","juuni","valge–roosakas","Punaselehised sordid ('Diabolo')","Ei"),
("Valge kontpuu","Cornus alba","Lehtpõõsas",1.2,2.5,"40–60 cm, C3",2.5,2,"Päike–poolvari","mai–juuni","valge; punased oksad","Talvine dekoratiivsus","Ei"),
("Van Houtte enelas","Spiraea × vanhouttei","Lehtpõõsas",1.2,2.5,"40–60 cm, C3",2,2,"Päike–poolvari","mai–juuni","valge",N,"Ei"),
("Hall enelas 'Grefsheim'","Spiraea × cinerea 'Grefsheim'","Lehtpõõsas",1,3,"40–60 cm, C3",1.5,1.5,"Päike","mai","valge","Varajane õitseja","Ei"),
("Jaapani enelas","Spiraea japonica","Lehtpõõsas",0.6,4,"20–30 cm, C2",0.8,0.8,"Päike–poolvari","juuli–aug","roosa","Sordid 'Goldflame', 'Little Princess' jt","Ei"),
("Põõsasmaran","Dasiphora fruticosa","Lehtpõõsas",0.7,3,"20–30 cm, C2",1,1,"Päike","juuni–sept","kollane / valge / roosa","Pikk õitsemine","Pärismaise liigi sort"),
("Thunbergi kukerpuu","Berberis thunbergii","Lehtpõõsas",0.8,4,"20–30 cm, C2",1.2,1,"Päike","mai","kollane","Okkaline; punaselehised sordid","Ei"),
("Läikiv tuhkpuu","Cotoneaster lucidus","Lehtpõõsas",1,4,"40–60 cm, paljasjuurne / P9",2,1.5,"Päike–poolvari","mai–juuni","roosakas; mustad viljad","Klassikaline pügatav hekk","Ei"),
("Alpi sõstar","Ribes alpinum","Lehtpõõsas",0.8,4,"40–60 cm, C2",1.2,1,"Päike–vari","mai","rohekaskollane","Varjutaluv hekk","Jah"),
("Harilik lumimari","Symphoricarpos albus","Lehtpõõsas",1,3,"30–40 cm, C2",1.5,1.5,"Päike–vari","juuni–aug","roosakas; valged viljad",N,"Ei"),
("Kurdlehine kibuvits","Rosa rugosa","Lehtpõõsas",1,3,"30–40 cm, C2",1.5,1.5,"Päike","juuni–sept","roosa / valge","Invasiivne võõrliik – mitte istutada rannikule ega looduse lähedale","Ei"),
("Pinnakatteroos","Rosa (pinnakattesordid)","Lehtpõõsas",0.6,N,"C2",0.5,1,"Päike","juuni–sept","mitmesugune",N,"Ei"),
("Aed-hortensia","Hydrangea paniculata","Lehtpõõsas",1.2,N,"40–60 cm, C5",2,1.8,"Päike–poolvari","juuli–sept","valge → roosa",N,"Ei"),
("Puishortensia 'Annabelle'","Hydrangea arborescens 'Annabelle'","Lehtpõõsas",1,N,"30–40 cm, C3",1.2,1.2,"Poolvari","juuli–sept","valge","Kevadel tagasi lõigata","Ei"),
("Õitsev vegeelia","Weigela florida","Lehtpõõsas",1.2,N,"30–40 cm, C3",1.5,1.5,"Päike–poolvari","juuni","roosa",N,"Ei"),
("Purpurpaju 'Nana'","Salix purpurea 'Nana'","Lehtpõõsas",0.8,4,"40–60 cm, C2",1.2,1,"Päike","aprill","hallikasroheline leht","Madal hekk, talub niiskust","Ei"),
("Päevaliilia","Hemerocallis","Püsik",0.5,N,"P11 / C2",0.7,0.6,"Päike–poolvari","juuli–aug","kollane / oranž / punane jt",N,"Ei"),
("Hosta","Hosta","Püsik",0.5,N,"C2",0.5,0.7,"Poolvari–vari","juuli–aug","lilla / valge; dekoratiivne leht","Laius sõltub sordist","Ei"),
("Aed-pojeng","Paeonia lactiflora","Püsik",0.8,N,"C3",0.8,0.9,"Päike","juuni","roosa / valge / punane",N,"Ei"),
("Purpur-siilkübar","Echinacea purpurea","Püsik",0.4,N,"P11 / C2",0.8,0.5,"Päike","juuli–sept","roosa",N,"Ei"),
("Kiirgav päevakübar 'Goldsturm'","Rudbeckia fulgida 'Goldsturm'","Püsik",0.4,N,"P11 / C2",0.6,0.5,"Päike","aug–sept","kollane",N,"Ei"),
("Faasseni kassinaeris","Nepeta × faassenii","Püsik",0.4,N,"P11",0.4,0.5,"Päike","juuni–sept","sinililla","Pärast 1. õitsemist tagasi lõigata","Ei"),
("Salu-salvei","Salvia nemorosa","Püsik",0.35,N,"P11",0.5,0.4,"Päike","juuni–aug","lilla",N,"Ei"),
("Kurereha 'Rozanne'","Geranium 'Rozanne'","Püsik",0.5,N,"P11 / C2",0.5,0.7,"Päike–poolvari","juuni–okt","sinililla","Väga pikk õitsemine","Ei"),
("Astilbe","Astilbe","Püsik",0.4,N,"P11 / C2",0.6,0.5,"Poolvari","juuli–aug","roosa / valge / punane","Vajab niisket mulda","Ei"),
("Aed-leeklill","Phlox paniculata","Püsik",0.5,N,"C2",0.9,0.6,"Päike–poolvari","juuli–aug","mitmesugune, lõhnav",N,"Ei"),
("Ahtalehine lavendel","Lavandula angustifolia","Püsik",0.35,N,"P11",0.4,0.4,"Päike","juuli–aug","lilla","Kuiv, lubjarikas muld","Ei"),
("Kõrge kukehari 'Herbstfreude'","Hylotelephium 'Herbstfreude'","Püsik",0.4,N,"P11 / C2",0.5,0.5,"Päike","aug–sept","roosa → punakaspruun","Põuakindel","Jah"),
("Siberi võhumõõk","Iris sibirica","Püsik",0.4,N,"P11",0.8,0.5,"Päike–poolvari","juuni","sinine / lilla / valge",N,"Ei"),
("Suur karikakar","Leucanthemum × superbum","Püsik",0.4,N,"P11",0.7,0.5,"Päike","juuli–aug","valge",N,"Ei"),
("Pehme kortsleht","Alchemilla mollis","Püsik",0.4,N,"P11",0.4,0.5,"Päike–poolvari","juuni–juuli","rohekaskollane","Hea ääristaim","Ei"),
("Teravaõiene kastik 'Karl Foerster'","Calamagrostis × acutiflora 'Karl Foerster'","Kõrreline",0.5,N,"C2 / C3",1.5,0.6,"Päike","juuli–sept","pruunikad õisikud","Püstine, talvel dekoratiivne","Ei"),
("Hiina siidpööris","Miscanthus sinensis","Kõrreline",0.8,N,"C3",1.8,1,"Päike","aug–okt","hõbedased õisikud","Kõrgus sõltub sordist","Ei"),
("Sinine aruhein","Festuca glauca","Kõrreline",0.25,N,"P9 / P11",0.25,0.3,"Päike","juuni","sinakashall leht",N,"Ei"),
("Väike igihali","Vinca minor","Pinnakate",0.3,N,"P9",0.15,0.5,"Poolvari–vari","mai","sinine","Igihaljas","Ei"),
("Jaapani pahhüsandra","Pachysandra terminalis","Pinnakate",0.25,N,"P9",0.2,0.3,"Poolvari–vari","mai","valge","Igihaljas","Ei"),
("Kaukaasia kukehari","Phedimus spurius","Pinnakate",0.25,N,"P9",0.1,0.3,"Päike","juuli","roosa / punane","Põuakindel","Jah"),
("Harilik toomingas","Padus avium","Lehtpuu",5,N,"10–12 cm ümbermõõt",10,6,"Päike–poolvari","mai","valge, lõhnav","Niiskem muld","Jah"),
("Künnapuu","Ulmus laevis","Lehtpuu",8,N,"16–18 cm ümbermõõt",20,12,"Päike–poolvari","aprill",N,"Talub linnatingimusi","Jah"),
("Harilik kadakas","Juniperus communis","Igihaljas põõsas",1,N,"60–80 cm, C5",3,1,"Päike",N,"sinakad käbimarjad","Sammasjad sordid 'Hibernica', 'Suecica'","Jah"),
("Kanarbik","Calluna vulgaris","Igihaljas põõsas",0.3,N,"P9",0.4,0.4,"Päike","aug–sept","roosa / lilla / valge","Happeline liivane muld","Jah"),
("Harilik sarapuu","Corylus avellana","Lehtpõõsas",2,2,"60–80 cm, C3",4,3,"Päike–poolvari","märts–aprill","urvad; pähklid","Vabakujuline hekk","Jah"),
("Harilik lodjapuu","Viburnum opulus","Lehtpõõsas",1.5,2,"40–60 cm, C3",3,2.5,"Päike–poolvari","mai–juuni","valge; punased viljad","Sort 'Roseum' (lumepall)","Jah"),
("Harilik kuslapuu","Lonicera xylosteum","Lehtpõõsas",1.2,3,"40–60 cm, C3",2,2,"Poolvari–vari","mai–juuni","kollakasvalge; punased viljad","Varjutaluv hekk; viljad mürgised","Jah"),
("Harilik türnpuu","Frangula alnus","Lehtpõõsas",1.5,2.5,"60–80 cm, C3",3,2,"Päike–poolvari","juuni","punased → mustad viljad","Kitsas sort 'Fine Line'","Jah"),
("Mailane kibuvits","Rosa majalis","Lehtpõõsas",1,3,"30–40 cm, C2",1.5,1.5,"Päike–poolvari","juuni","roosa; punased kibuvitsamarjad","Annab juurevõsusid","Jah"),
("Üheemakaline viirpuu","Crataegus monogyna","Lehtpõõsas",1.5,4,"60–80 cm, paljasjuurne",4,3,"Päike","mai–juuni","valge; punased viljad","Okkaline pügatav hekk","Jah"),
("Harilik kikkapuu","Euonymus europaeus","Lehtpõõsas",1.5,N,"40–60 cm, C3",3,2,"Päike–poolvari","mai","roosad viljad; punane sügisvärv","Mürgine","Jah"),
("Harilik näsiniin","Daphne mezereum","Lehtpõõsas",0.8,N,"C2",1,0.8,"Poolvari","aprill","roosa, lõhnav; punased viljad","Väga mürgine","Jah"),
("Lapi paju","Salix lapponum","Lehtpõõsas",1,N,"C2",1,1,"Päike","aprill–mai","hõbehall leht","Niiske muld","Jah"),
("Harilik nurmenukk","Primula veris","Püsik",0.25,N,"P9",0.2,0.2,"Päike–poolvari","mai","kollane","Lubjarikas muld","Jah"),
("Verev kurereha","Geranium sanguineum","Püsik",0.4,N,"P11",0.3,0.5,"Päike","juuni–aug","purpurroosa","Põuakindel","Jah"),
("Aas-kurereha","Geranium pratense","Püsik",0.5,N,"P11",0.6,0.5,"Päike","juuni–juuli","sinililla",N,"Jah"),
("Mets-kurereha","Geranium sylvaticum","Püsik",0.4,N,"P11",0.5,0.4,"Poolvari","juuni","lilla",N,"Jah"),
("Kerakellukas","Campanula glomerata","Püsik",0.3,N,"P11",0.5,0.3,"Päike–poolvari","juuni–juuli","lilla",N,"Jah"),
("Harilik kurekell","Aquilegia vulgaris","Püsik",0.3,N,"P11",0.6,0.3,"Poolvari","juuni","sinililla","Külvab ise","Jah"),
("Harilik raudrohi","Achillea millefolium","Püsik",0.35,N,"P11",0.5,0.4,"Päike","juuli–sept","valge / roosa (sordid)","Põuakindel","Jah"),
("Harilik härjasilm","Leucanthemum vulgare","Püsik",0.3,N,"P11",0.5,0.3,"Päike","juuni–juuli","valge",N,"Jah"),
("Aasnelk","Dianthus deltoides","Püsik",0.25,N,"P9",0.2,0.3,"Päike","juuni–aug","roosa / punane","Kuiv muld","Jah"),
("Harilik merikann","Armeria maritima","Püsik",0.25,N,"P9",0.25,0.25,"Päike","juuni–juuli","roosa","Kuiv liivane muld","Jah"),
("Värv-karikakar","Anthemis tinctoria","Püsik",0.35,N,"P11",0.5,0.4,"Päike","juuli–aug","kollane","Kuiv muld","Jah"),
("Must tulikas","Verbascum nigrum","Püsik",0.4,N,"P11",1,0.4,"Päike","juuli–aug","kollane",N,"Jah"),
("Harilik kuldvits","Solidago virgaurea","Püsik",0.35,N,"P11",0.6,0.3,"Päike–poolvari","aug–sept","kollane","NB! Mitte segi ajada invasiivse kanada kuldvitsaga","Jah"),
("Harilik kullerkupp","Trollius europaeus","Püsik",0.4,N,"P11",0.5,0.4,"Päike–poolvari","mai–juuni","kollane","Niiske muld","Jah"),
("Harilik varsakabi","Caltha palustris","Püsik",0.4,N,"P11",0.3,0.4,"Päike–poolvari","mai","kollane","Märg muld, veeserv","Jah"),
("Kollane võhumõõk","Iris pseudacorus","Püsik",0.5,N,"C2",1,0.5,"Päike–poolvari","juuni","kollane","Veeserv, vihmapeenar","Jah"),
("Harilik kukesaba","Lythrum salicaria","Püsik",0.5,N,"P11 / C2",1.2,0.5,"Päike","juuli–aug","purpurroosa","Niiske muld, vihmapeenar","Jah"),
("Harilik angervaks","Filipendula ulmaria","Püsik",0.5,N,"P11 / C2",1.2,0.6,"Päike–poolvari","juuli","valge, lõhnav","Niiske muld","Jah"),
("Harilik ussitatar","Bistorta officinalis","Püsik",0.4,N,"P11",0.6,0.4,"Päike–poolvari","juuni","roosa","Niiske muld","Jah"),
("Harilik kopsurohi","Pulmonaria obscura","Püsik",0.3,N,"P11",0.25,0.3,"Poolvari–vari","aprill–mai","roosa → sinine",N,"Jah"),
("Sinilill","Hepatica nobilis","Püsik",0.2,N,"P9",0.15,0.2,"Poolvari–vari","aprill","sinine",N,"Jah"),
("Jaanalind","Matteuccia struthiopteris","Püsik",0.6,N,"C2",1,0.8,"Poolvari–vari",N,"sõnajalg","Niiske muld; levib","Jah"),
("Ohtene kilpjalg","Dryopteris filix-mas","Püsik",0.6,N,"C2",0.8,0.8,"Poolvari–vari",N,"sõnajalg",N,"Jah"),
("Luht-kastevars","Deschampsia cespitosa","Kõrreline",0.4,N,"P11 / C2",0.6,0.4,"Päike–poolvari","juuni–aug","kuldsed õisikud",N,"Jah"),
("Sinihelmikas","Molinia caerulea","Kõrreline",0.5,N,"C2",0.8,0.5,"Päike–poolvari","aug–sept","kuldne sügisvärv","Niiske muld","Jah"),
("Lamba-aruhein","Festuca ovina","Kõrreline",0.25,N,"P9",0.25,0.25,"Päike","juuni","sinakasroheline","Kuiv liivane muld","Jah"),
("Harilik leesikas","Arctostaphylos uva-ursi","Pinnakate",0.4,N,"P9",0.1,1,"Päike","mai","valge; punased viljad","Igihaljas; kuiv liivane muld","Jah"),
("Harilik pohl","Vaccinium vitis-idaea","Pinnakate",0.25,N,"P9",0.2,0.3,"Päike–poolvari","juuni","valkjasroosa; punased marjad","Igihaljas; happeline muld","Jah"),
("Maikelluke","Convallaria majalis","Pinnakate",0.2,N,"P9",0.2,0.3,"Poolvari–vari","mai","valge, lõhnav","Mürgine; levib agaralt","Jah"),
("Võsaülane","Anemone nemorosa","Pinnakate",0.15,N,"P9",0.15,0.2,"Poolvari–vari","aprill–mai","valge","Kevadine; suvel kaob","Jah"),
("Liivatee","Thymus serpyllum","Pinnakate",0.25,N,"P9",0.1,0.3,"Päike","juuli","roosa","Kuiv liivane muld","Jah"),
("Harilik kukehari","Sedum acre","Pinnakate",0.2,N,"P9",0.08,0.3,"Päike","juuni–juuli","kollane","Väga põuakindel; haljaskatus","Jah"),
("Kahekojaline kassikäpp","Antennaria dioica","Pinnakate",0.2,N,"P9",0.1,0.25,"Päike","mai–juuni","roosa / valge","Kuiv vaene muld","Jah"),
("Mets-maasikas","Fragaria vesca","Pinnakate",0.25,N,"P9",0.15,0.3,"Päike–poolvari","mai–juuni","valge; marjad",N,"Jah"),
]

wb = Workbook(); ws = wb.active; ws.title = "Taimed"
ws.append(COLS)
for r in R:
    name, lat, typ, sp, hk, form, h, w, light, bloom, fl, note, nat = r
    ws.append([name, lat, typ, sp, hk, form, None, h, w, light, bloom, fl, note, nat, None, None])
for c in ws[1]:
    c.font = Font(bold=True); c.fill = PatternFill("solid", fgColor="EEF1EA")
for row in ws.iter_rows(min_row=2, min_col=7, max_col=7):
    for c in row: c.fill = PatternFill("solid", fgColor="FFF6CC"); c.number_format = "0.00"
widths = [30, 34, 18, 14, 12, 26, 11, 10, 9, 16, 14, 30, 40, 18, 16, 18]
for i, wd in enumerate(widths):
    ws.column_dimensions[chr(65 + i)].width = wd
ws.freeze_panes = "B2"
dv = DataValidation(type="list", formula1='"püsik-padi,püsik-püstine,tõlvik,kõrreline,põõsas,okaspõõsas,puu,okaspuu,pinnakate"', allow_blank=True)
ws.add_data_validation(dv); dv.add(f"O2:O{len(R)+200}")

info = wb.create_sheet("Juhend")
for line in [
    "Taimede andmebaas haljastuse tööriistale.",
    "Kollane veerg 'Hind (€/tk)' – sinu hinnad ilma käibemaksuta.",
    "Uue taime lisamiseks lisa rida lehe 'Taimed' lõppu. Kohustuslikud: Taim, Ladinakeelne nimi, Tüüp, Istutusvahe, Kõrgus, Laius.",
    "Õitseb: kuud kujul 'juuni–aug' või 'mai'. Õis / dekoratiivsus: värvisõnad (valge, kollane, roosa, lilla, sinine, punane, oranž ...).",
    "Kuju (valikuline): kui automaatne kuju illustratsioonil ei sobi, vali: püsik-padi, püsik-püstine, tõlvik, kõrreline, põõsas, okaspõõsas, puu, okaspuu, pinnakate.",
    "Õievärv hex (valikuline): nt #d23a6e, kui tahad illustratsioonil täpset värvi.",
]:
    info.append([line])
info.column_dimensions["A"].width = 120
wb.save("/home/claude/haljastus/data/taimed.xlsx")
print(len(R), "taime")
