from django.test import TestCase

# Create your tests here.
if __name__ == '__main__':
    try:
        1/0
    except Exception as e:
        print(e)

