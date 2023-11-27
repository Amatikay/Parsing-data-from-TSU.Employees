#include<iostream>
#include<string>
#include<vector>
#include<fstream>
#include<sstream>
#include <algorithm>


/*
Таблица с Subdivision_name;SubdivisionID доступна в ./Data/

Классификация:
0	Естественные науки и математика
1	Инженерные науки и технологии
2	Медицинские науки
3	Биотехнические науки
4	Общественные науки
5	Гуманитарные науки
6	Междисциплинарные исследования

0 - 1 2 3
1 - 3 4 5
2 - 7 8 9
.
.
.
...

Массив словарей.
Если рассматриваемое значение находится в словаре - меняю значение на индекс словаря.

Формат файла с данными классификации:
1 2 3
4 5 6
7 8 9
*/

std::vector<int> getVectorFromString(const std::string& line){
	std::istringstream iss(line);
	std::vector<int> IDs_v;
	int num;
	while(iss >> num){
		IDs_v.push_back(num);
	}

	return IDs_v;
}

int getCluster(const std::vector<std::vector<int>>& data, int _id) {
    for (size_t i = 0; i < data.size(); ++i) {
        if (std::find(data[i].begin(), data[i].end(), _id) != data[i].end()) {
            return i;
        }
    }
    return -1;
}

int main(int argc, char *argv[]){
	std::vector<std::vector<int>> cluster;
	
	std::ifstream ClusterID_SubdivsIDs(argv[1]);
	if (ClusterID_SubdivsIDs.is_open()){
		std::string line;
		while (std::getline(ClusterID_SubdivsIDs,line)){
//			std::istringstream iss(line);
			cluster.push_back(getVectorFromString(line));
        }
		ClusterID_SubdivsIDs.close();
	}

	// for (const auto& i : cluster){
		// for (int j : i){
			// std::cout<< j << ' ';
		// }
		// std::cout << std::endl;
	// }

	std::ifstream SubdivsID(argv[2]);
	std::ofstream ClusterSubdiv("clusterSubdiv.dat");
	if (SubdivsID.is_open() && ClusterSubdiv.is_open()  ){
	std::string line;
		while(std::getline(SubdivsID,line)){
			ClusterSubdiv<< getCluster(cluster,stoi(line))<< std::endl;
		}
	}
	SubdivsID.close();
	ClusterSubdiv.close();
	

	return 0;
}
