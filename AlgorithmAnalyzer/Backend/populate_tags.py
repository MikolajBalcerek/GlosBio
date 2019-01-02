from main import app

app.config.from_object('config.DevelopmentConfig')

sm = app.config['SAMPLE_MANAGER']

tags = {
    "age": ["< 20", "20 - 40", "40 - 60", "> 60"],
    "gender": ["male", "female"]
    }

print("populate logs...")
for tag_name in tags:
    sm.add_tag(tag_name, tags[tag_name])
print("fin...")
