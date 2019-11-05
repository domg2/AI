#include "NL_ParkDetector.h"
#include <iostream>
#include <string>
#include <fstream>
#include <vector>
#include <opencv2/opencv.hpp>
using namespace std;
using namespace cv;

//#define SHOW
int main(int argc, char **argv)
{
	int dwReturn = -1;
	// -------------------ģ�ͼ��ء���ʼ�����ڴ���㡢����-------------------//
	char RootPath[256] = ".";

	NLDJ_PD_Handle djHandle_PD;
	NLDJ_PD_VarOut pdjVarOut;
	NLDJ_PD_VarIn pdjVarIn;
	int modeID = 0; // CPU
	dwReturn = NL_PD_Command(&djHandle_PD, RootPath);
	if (dwReturn != 0)
	{
		printf("command error!");
		return dwReturn;
	}

	string djStrImgPath = "./data/3.jpg";
	Mat InMat = imread(djStrImgPath.c_str());
	if (InMat.empty())
	{
		printf("Load image fail!");
		NL_PD_UnloadModel(&djHandle_PD);
		return -3001;
	}

	printf("load model done.\n");
	//-------------------------------//
	std::ofstream djResultout;
	djResultout.open("./test/testResult.txt", std::ios::out);
	djResultout << djStrImgPath << endl;
	pdjVarIn.dwChannel = InMat.channels();
	pdjVarIn.dwHeight = InMat.rows;
	pdjVarIn.dwWidth = InMat.cols;
	pdjVarIn.pubyIm = InMat.data;
	djResultout << InMat.rows << "," << InMat.cols << "," << InMat.channels();

#ifdef TIME
	double start = (double)cv::getTickCount();
#endif
	dwReturn = NL_PD_Process(&djHandle_PD, &pdjVarIn, &pdjVarOut);
#ifdef TIME
	start = (double)cv::getTickCount() - start;
	cout << " " << start * 1000. / (cv::getTickFrequency()) << endl;
#endif

	// show the result
	cv::Scalar color;
	cv::Rect djrect;
	for (int i = 0; i < pdjVarOut.parkNum; i++)
	{
		if (pdjVarOut.pdwStatus[i] == 0)
			color = cv::Scalar(0, 255, 0); //green empty
		else
			color = cv::Scalar(0, 0, 255); //red occupied

		djrect.x = pdjVarOut.pdjPositon[i].x;
		djrect.y = pdjVarOut.pdjPositon[i].y;
		djrect.width = pdjVarOut.pdjPositon[i].width;
		djrect.height = pdjVarOut.pdjPositon[i].height;
		djResultout << "Park Position" << (i + 1) << " Status: " << pdjVarOut.pdwStatus[i] << endl;

		cv::rectangle(InMat, djrect, color, 2, 8, 0);
		cv::putText(InMat, to_string(pdjVarOut.pfScore[i]), cv::Point(djrect.x, djrect.y), cv::FONT_HERSHEY_SIMPLEX, 0.8, cv::Scalar(255, 0, 0), 2, 2);
		//printf("parking pdwStatus :%d, score :%f\n", pdjVarOut.pdwStatus[i], pdjVarOut.pfScore[i]);
#ifdef SHOW
		cv::namedWindow("result", CV_WINDOW_NORMAL);
		imshow("result", InMat);
		cv::waitKey(0);
#endif
	}
	imwrite("InMat.jpg", InMat);
	djResultout.close();
	//release memory
	dwReturn = NL_PD_UnloadModel(&djHandle_PD);
	if (dwReturn < 0)
	{
		return -1;
	}
	return 0;
}
