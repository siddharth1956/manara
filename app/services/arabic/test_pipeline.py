from app.services.arabic.pipeline import ArabicPipeline

pipeline = ArabicPipeline()

question = "ما هو متوسط الغطاء السحابي في دبي؟"

result = pipeline.analyze(question)

print(result)