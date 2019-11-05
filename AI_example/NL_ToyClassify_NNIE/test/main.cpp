#include "NL_ToyClassify.h"
#include <iostream>
#include <string>
#include <fstream>
#include <vector>
#include <opencv2/opencv.hpp>
using namespace std;
using namespace cv;

#ifndef __linux__
// for windows access()
#include <io.h>
#else
#include <unistd.h>
#endif

//#define SHOW
#define WINDOW_NAME "windowsName"
//------------------------------------------------------------------------------------------------
int main(int argc, char **argv)
{

	int dwReturn = -1;
	//
	//����ͼƬ���ı�
	string djStrImgListPath = "./test/testlist.txt";
	//���ͼƬ�����ļ���
	string djStrBasicPath = "./data/";
#ifndef __linux__
	if (_access(djStrImgListPath.c_str(), 0) == -1)
	{
		fprintf(stdout, "test/testlist.txt UNEXIST\n");
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

	printf("load model done.\n");
	//-------------------------------//
	//detection result file
	std::ofstream djResultout;
	djResultout.open("./test/testResult.txt", std::ios::out);
	Mat InMat;
	for (int i = 0; i < dwImgNum; i++)
	{
		//load image
		djStrImgPath = djStrBasicPath + djVecPaths[i];
		InMat = imread(djStrImgPath.c_str());
		djResultout << djStrImgPath;
		if (InMat.empty())
		{
			printf("Load image fail!\n");
			NL_TC_UnloadModel(&djHandle_TC);
			return -3001;
		}
		//
		pdjVarIn.dwChannel = InMat.channels();
		pdjVarIn.dwHeight = InMat.rows;
		pdjVarIn.dwWidth = InMat.cols;
		pdjVarIn.pubyIm = InMat.data;
		djResultout << "," << InMat.rows << "," << InMat.cols << "," << InMat.channels();

#ifdef TIME
		double start = (double)cv::getTickCount();
#endif
		dwReturn = NL_TC_Process(&djHandle_TC, &pdjVarIn, &pdjVarOut);
#ifdef TIME
		start = (double)cv::getTickCount() - start;
		cout << " " << start * 1000. / (cv::getTickFrequency()) << endl;
#endif

		cv::Scalar color;
		cv::Rect djrect;
		for (int i = 0; i < pdjVarOut.dwNum; i++)
		{
			string outPredict = pdjVarOut.dsClassName[i];
			float scores = pdjVarOut.dqScores[i];
			//std::cout << std::fixed << std::setprecision(4) << scores
			std::cout << outPredict << " - \"" << scores << "\"" << std::endl;
			cv::putText(InMat, outPredict, cv::Point(10, 15 * (i + 1)), cv::FONT_HERSHEY_SIMPLEX, 0.8, cv::Scalar(255, 0, 0), 2, 2);
		}

		//cout<<pdjVarOut.dwNum<<endl;
		djResultout << "," << pdjVarOut.dwNum;
		for (int p = 0; p < pdjVarOut.dwNum; p++)
		{
			string outPredict = pdjVarOut.dsClassName[i];
			float scores = pdjVarOut.dqScores[i];
			djResultout << "Top" << (p + 1) << " Class: " << outPredict << "Scores:" << scores << endl;
#ifdef SHOW
			cv::putText(InMat, outPredict, cv::Point(10, 15 * (i + 1)), cv::FONT_HERSHEY_SIMPLEX, 0.8, cv::Scalar(255, 0, 0), 2, 2);
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
	djResultout.close();
	//release memory
	dwReturn = NL_TC_UnloadModel(&djHandle_TC);

	if (dwReturn < 0)
	{
		return -1;
	}
	return 0;
}
