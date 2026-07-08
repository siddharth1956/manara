from app.services.arabic_nlu import ArabicNLU

nlu = ArabicNLU()

queries = [

    "اعرض صور Sentinel",

    "ما متوسط الغطاء السحابي",

    "قارن بين Sentinel-2A و Sentinel-2B",

    "أين تقع دبي",

    "اعرض الطرق في دبي"

]

for q in queries:

    print("=" * 40)

    print(q)

    print(nlu.classify(q))