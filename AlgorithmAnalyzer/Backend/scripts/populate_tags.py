import os

os.sys.path.append('..')
from main import app

app.config.from_object('config.DevelopmentConfig')

sm = app.config['SAMPLE_MANAGER']

tags = {
    "age": ["< 20", "20 - 40", "40 - 60", "> 60"],
    "gender": ["male", "female"],
    "language": ["polish", "english", "german"]
    }

print("populate logs...")
for tag_name in tags:
    try:
        sm.add_tag(tag_name, tags[tag_name])
        print(f"added tag {tag_name}")
    except ValueError as e:
        print(str(e))
        continue
print("fin...")
