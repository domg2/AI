#include "NL_ToyClassify.h"
#include <iostream>
#include <string>
#include <fstream>
#include <vector>
#include <opencv2/opencv.hpp>
#include <strstream>
using namespace std;
using namespace cv;

#ifndef __linux__
// for windows access()
#include <io.h>
#else
#include <unistd.h>
#endif

//#define SHOW 1
//------------------------------------------------------------------------------------------------
int main(int argc, char **argv)
{

	int dwReturn = -1;
	//
	//����ͼƬ���ı�
	string djStrImgListPath = "./test/ToyClassifyList.txt";
	//���ͼƬ�����ļ���
	string djStrBasicPath = "./data/";
#ifndef __linux__
	if (_access(djStrImgListPath.c_str(), 0) == -1)
	{
		fprintf(stdout, "test/ToyClassifyList.txt UNEXIST\n");
		return -1001;
	}
#else
	if (access(djStrImgListPath.c_str(), 0) == -1)
	{
		fprintf(stdout, "test/ToyClassifyList.txt UNEXIST\n");
		return -1001;
	}
#endif

	string djStrImgPath;
	ifstream ifImgtxtread(djStrImgListPath.c_str());
	vector<string> djVecPaths;
	while (getline(ifImgtxtread, djStrImgPath))
	{
		djVecPaths.push_back(djStrImgPath);
	}
	int dwImgNum = djVecPaths.size();

	// --------------------------------------//
	char pbyModelPath[256] = ".";
	NLDJ_TC_Handle djHandle_TC;
	NLDJ_TC_VarIn pdjVarIn;
	NLDJ_TC_VarOut pdjVarOut;
	dwReturn = NL_TC_Command(&djHandle_TC, pbyModelPath);
	if (dwReturn != 0)
	{
		printf("command error\n");
		return dwReturn;
	}

	NL_TC_Init(&djHandle_TC);
	if (dwReturn < 0)
	{
		printf("init memory error\n");
		//NL_TC_Exit(&djHandle_TC);
		NL_TC_UnloadModel(&djHandle_TC);
		return dwReturn;
	}
	//-------------------------------//
	//detection result file
	std::ofstream djResultout;
	djResultout.open("./test/testResult.txt", std::ios::out);
	Mat InMat;
	int topPrcNum = 2; //���Ԥ����ǰ����
	for (int i = 0; i < dwImgNum; i++)
	{
		//load image
		string dsTmp;
		istrstream strin(djVecPaths[i].c_str());
		strin >> dsTmp;
		djStrImgPath = djStrBasicPath + dsTmp;
		//djStrImgPath = djStrBasicPath + djVecPaths[i];
		InMat = imread(djStrImgPath.c_str());
		djResultout << djStrImgPath;
		if (InMat.empty())
		{
			printf("Load image fail!");
			NL_TC_UnloadModel(&djHandle_TC);
			return -3001;
		}
		//
		pdjVarIn.dwChannel = InMat.channels();
		pdjVarIn.dwHeight = InMat.rows;
		pdjVarIn.dwWidth = InMat.cols;
		pdjVarIn.pubyIm = InMat.data;
		pdjVarIn.dwPreNum = topPrcNum;
		djResultout << "," << InMat.rows << "," << InMat.cols << "," << InMat.channels() << endl;

#ifdef TIME
		double start = (double)cv::getTickCount();
#endif
		dwReturn = NL_TC_Process(&djHandle_TC, &pdjVarIn, &pdjVarOut);
#ifdef TIME
		start = (double)cv::getTickCount() - start;
		cout << " " << start * 1000. / (cv::getTickFrequency()) << endl;
#endif
		djResultout << pdjVarOut.dwNum << endl;
		cv::Scalar color;
		cv::Rect djrect;
		for (int p = 0; p < pdjVarOut.dwNum; p++)
		{
			string outPredict = pdjVarOut.dsClassName[p];
			float scores = pdjVarOut.dqScores[p];
			std::cout << " Class Name: " << outPredict << " Scores: " << scores << std::endl;
			djResultout << " Class Name: " << outPredict << " Scores: " << scores << std::endl;
#ifdef SHOW
			cv::putText(InMat, outPredict, cv::Point(10, 15 * (p + 1)), cv::FONT_HERSHEY_SIMPLEX, 0.8, cv::Scalar(255, 0, 0), 2, 2);
#endif
		}
#ifdef SHOW
		cv::namedWindow("result", CV_WINDOW_NORMAL);
		imshow("result", InMat);
		cv::waitKey(0);
#endif
		if (dwReturn < 0)
		{
			return dwReturn;
		}
	}
	//release memory
	djResultout.close();
	dwReturn = NL_TC_UnloadModel(&djHandle_TC);

	if (dwReturn < 0)
	{
		return -1;
	}
	return 0;
}
