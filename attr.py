class MyClass:
    def __init__(self):
        self.attribute = 5

obj = MyClass()
value = getattr(obj, 'attribute', None)
if value is None:
    print("Attribute not found:")  # Output: Attribute value: 5
# else:
#     print("Attribute not found")
