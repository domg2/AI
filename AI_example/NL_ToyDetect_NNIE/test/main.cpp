#include "NL_ToyDetection.h"
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

// #define SHOW
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
		fprintf(stdout, "test/ToyDetectionList.txt UNEXIST\n");
		return -1001;
	}
#else
	if (access(djStrImgListPath.c_str(), 0) == -1)
	{
		fprintf(stdout, "test/ToyDetectionList.txt UNEXIST\n");
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
	NLDJ_TD_Handle djHandle_TD;
	NLDJ_TD_VarIn pdjVarIn;
	NLDJ_TD_VarOut pdjVarOut;
	int dwSize = 416;
	dwReturn = NL_TD_Command(&djHandle_TD, pbyModelPath);
	if (dwReturn != 0)
	{
		printf("command error\n");
		return dwReturn;
	}

	NL_TD_Init(&djHandle_TD);
	if (dwReturn < 0)
	{
		printf("init memory error\n");
		//NL_TD_Exit(&djHandle_TD);
		NL_TD_UnloadModel(&djHandle_TD);
		return dwReturn;
	}
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
		cout << djStrImgPath;
		if (InMat.empty())
		{
			printf("Load image fail!");
			NL_TD_UnloadModel(&djHandle_TD);
			return -3001;
		}
		//
		pdjVarIn.dwChannel = InMat.channels();
		pdjVarIn.dwHeight = InMat.rows;
		pdjVarIn.dwWidth = InMat.cols;
		pdjVarIn.pubyIm = InMat.data;
		cout << "," << InMat.rows << "," << InMat.cols << "," << InMat.channels() << "," << endl;
		djResultout << "," << InMat.rows << "," << InMat.cols << "," << InMat.channels() << "," << endl;

#ifdef TIME
		double start = (double)cv::getTickCount();
#endif
		dwReturn = NL_TD_Process(&djHandle_TD, &pdjVarIn, &pdjVarOut);
#ifdef TIME
		start = (double)cv::getTickCount() - start;
		cout << " " << start * 1000. / (cv::getTickFrequency()) << endl;
#endif

		for (int j = 0; j < pdjVarOut.dwObjectSize; j++)
		{
			NLDJ_TD_ObjInfor outObject = pdjVarOut.pdjToyInfors[j];
			std::cout << "Object name : " << outObject.className << " , Score: " << outObject.fscore << " positon: "
					  << outObject.dwLeft << "," << outObject.dwTop << ","
					  << outObject.dwRight << "," << outObject.dwBottom << std::endl;
			djResultout << "Object name : " << outObject.className << " , Score: " << outObject.fscore << " positon: "
						<< outObject.dwLeft << "," << outObject.dwTop << ","
						<< outObject.dwRight << "," << outObject.dwBottom << std::endl;
			char label[100];
			sprintf(label, "%s,%f", outObject.className, outObject.fscore);
			int baseline;
			cv::Size size = cv::getTextSize(label, cv::FONT_HERSHEY_SIMPLEX, 0.5, 0, &baseline);
			cv::Point pt1, pt2;
			pt1.x = outObject.dwLeft;
			pt1.y = outObject.dwTop;
			pt2.x = outObject.dwRight;
			pt2.y = outObject.dwBottom;
			int index = outObject.dwClassID;
			int green = 255 * ((index + 1) % 3);
			int blue = 255 * (index % 3);
			int red = 255 * ((index + 1) % 2);
			//cout << pt1.x << " --" << pt1.y << " --" << pt2.x << " --" << pt2.y << endl;
#ifdef SHOW
			cv::rectangle(InMat, pt1, pt2, cvScalar(red, green, blue), 5, 8, 0);
			cv::putText(InMat, label, pt1, cv::FONT_HERSHEY_SIMPLEX, 0.5, cv::Scalar(0, 0, 0));
#endif
		}
#ifdef SHOW
		cv::namedWindow("result", CV_WINDOW_AUTOSIZE);
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
	dwReturn = NL_TD_UnloadModel(&djHandle_TD);

	if (dwReturn < 0)
	{
		return -1;
	}
	return 0;
}
