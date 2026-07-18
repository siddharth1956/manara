from app.services.arabic.intent import ArabicIntentClassifier
classifier = ArabicIntentClassifier()

questions = [

    "ما هو متوسط الغطاء السحابي؟",

    "اعرض النباتات في دبي",

    "اعرض الطرق في الشارقة",

    "ابحث عن صور سنتينل"

]

for q in questions:

    print("-" * 50)

    print("Question:", q)

    print("Intent:", classifier.classify(q))