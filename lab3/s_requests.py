import requests

# GET
response_get = requests.get("http://localhost:5000/number/", params={"param": 5})
print("GET:", response_get.json())

# POST
response_post = requests.post("http://localhost:5000/number/", json={"jsonParam": 3})
print("POST:", response_post.json())

# DELETE
response_delete = requests.delete("http://localhost:5000/number/")
print("DELETE:", response_delete.json())
