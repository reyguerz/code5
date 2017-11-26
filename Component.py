__author__ = 'Rey Guerrero'

#*****  Model of Components

#**
import VarList
import WindTBWvsP
import random

def Solar_PV_Out(Irradiance, Temperature): # computation for temperature is in terms of Celsius
	
	NOCT = VarList.NOCT
	PVEff = VarList.PVEff
	PVatSTC = VarList.PVatSTC
	PVTempCoeff = VarList.PVTempCoeff

	PVTemp = (Temperature - 273) + (NOCT - 20) * (Irradiance/800)
	powerout = PVEff *(Irradiance/1000)*PVatSTC*((PVTemp - 25)*PVTempCoeff + 1 )

	return powerout


#*** Search Method
# used in Wind TB Out 
def SearchLUTBisectionMethod(LUTContent, LUT): 
	maxindex = len(LUT)-1
	minindex = 0
	index = random.randrange(len(LUT))
	direction = 2
	Loop = 1
	SearchResult = []

	while Loop == 1:
		if LUTContent < LUT[index]:
			maxindex = index
		elif LUTContent > LUT[index]:
			minindex = index
		else:
			direction = 0
			Loop = 0
			break

		if (maxindex - minindex == 1):
			if index == maxindex:
				direction = -1
			elif index == minindex:
				direction = 1
			Loop = 0
		else:
			index = round((maxindex + minindex)/2)
			direction = 0
		


	SearchResult.append(index)
	SearchResult.append(direction)

	return SearchResult


def Wind_TB_Out(WindSpeed):

	WindTBMaxWindSpeed = WindTBWvsP.MaxWindSpeed
	WindTBLUTW = WindTBWvsP.LUTWindSpeed
	WindTBLUTP = WindTBWvsP.LUTPout



	if (WindSpeed < WindTBMaxWindSpeed):

		SearchResult = SearchLUTBisectionMethod(WindSpeed, WindTBLUTW)

		if SearchResult[1] != 0:
			a = int(SearchResult[0])
			b = int(SearchResult[0] + SearchResult[1])
			#linear interpolation
			m = (WindTBLUTP[b] - WindTBLUTP[a]) / ( WindTBLUTW[b] - WindTBLUTW[a]) # slope
			powerout = WindTBLUTP[a] + (WindSpeed - WindTBLUTW[a]) * m
			#print("a: ",a," b: ",b)
		else:
			#print(SearchResult[0])
			powerout = WindTBLUTP[int(SearchResult[0])]

	else:
		powerout = WindTBMaxPower 

	return powerout