from api.MarvinClient import Marvin

def main():
    marvin = Marvin()
    marvin_map = marvin.get_api('name=12772-12705')
    print(marvin_map)

if __name__ == '__main__':
    main()