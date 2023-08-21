from pytool import *
import json

# define agent in globals for custom self JavaAgent
agent = JavaAgent()
if __name__ == '__main__':
    print(json.dumps(variables(), indent=2))
