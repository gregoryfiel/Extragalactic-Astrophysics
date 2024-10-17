from api.MarvinClient import Marvin

def main():
    marvin = Marvin()
    marvin_map = marvin.get_api('8485-1901', 'SPX', 'MILESHC-MASTARSSP')
    print(marvin_map)

if __name__ == '__main__':
    main()
