from app.services.language_detector import detect_language

queries = [

    "Show Sentinel images",

    "اعرض صور Sentinel",

    "Average cloud cover",

    "ما متوسط الغطاء السحابي",

    "Compare Sentinel-2A and Sentinel-2B",

    "قارن بين Sentinel-2A و Sentinel-2B"

]

for q in queries:

    print("=" * 40)

    print(q)

    print(detect_language(q))