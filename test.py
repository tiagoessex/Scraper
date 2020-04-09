
import scraping


s = scraping.Scrapping()	

try:
	r = s.scrap("Restaurante Capa Negra", 506036944)
	print (r)
except Exception as e:
	print (e)


