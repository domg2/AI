#include "LPKernelEx.h"
#include <stdlib.h>
#include <string>
#include <fstream>
#include <vector>
#include <opencv2/opencv.hpp>
using namespace std;

#include <cstdlib>
#include <memory>
#include <string>

int main()
{
	int dwReturn = -1;
	//cvNamedWindow("test", 0);
	//----------------初始化---------------//
	char pbyModelPath[256] = "./";
	dwReturn = LPR_InitEx(pbyModelPath);
	if (dwReturn != 0)
	{
		std::cout << "Failed to initial,code : " << dwReturn << std::endl;
		return 0;
	}
	//--------------批量读图--------------//
	string djStrImgListPath = "./testDate.txt"; // 测试图片名
	string djStrBasicPath = "./testDate/";		// 测试图片路径
	ifstream ifImgtxtread(djStrImgListPath.c_str());
	vector<string> djVecPaths;
	string djStrImgPath;
	while (getline(ifImgtxtread, djStrImgPath))
	{
		djVecPaths.push_back(djStrImgPath);
	}
	int dwImgNum = djVecPaths.size();

	std::ofstream djResultout;
	djResultout.open("./PlateDetectResult.txt", std::ios::out);
	NL_PlateDet_VarIn pdjVarIn;
	NL_PlateDet_VarOut pdjVarOut; // 保存输出车牌结果
	int nRecogNum = 0;			  // 输出检测到的车牌，0或1
	//--------------批量处理--------------//
	for (int i = 0; i < dwImgNum; i++)
	{
		//load image
		djStrImgPath = djStrBasicPath + djVecPaths[i];
		cout << djStrImgPath << endl;
		djResultout << djStrImgPath << endl;
		;
		cv::Mat srcMat = cv::imread(djStrImgPath);
		if (srcMat.empty())
		{
			std::cout << "Failed to read image：" << djStrImgPath << std::endl;
			continue;
		}
		pdjVarIn.djObjRect = {20, 20, 100, 100};
		pdjVarIn.dwChannel = srcMat.channels();
		pdjVarIn.pubyIm = srcMat.data;
		pdjVarIn.dwHeight = srcMat.rows;
		pdjVarIn.dwWidth = srcMat.cols;
		pdjVarIn.dwThredTime = 1000;
		djResultout << srcMat.rows << "," << srcMat.cols << "," << srcMat.channels() << endl;

		// 识别模块
		double beginTime = (double)cv::getTickCount();
		dwReturn = LPR_FileEx(&pdjVarIn, &pdjVarOut, nRecogNum);
		beginTime = ((double)cv::getTickCount() - beginTime) * 1000. / (cv::getTickFrequency());
		djResultout << "useTime:" << beginTime << endl;
		std::cout << "useTime:" << beginTime << endl;
		// 结果输出
		if (dwReturn == 0 && nRecogNum > 0)
		{
			std::string pathname = pdjVarOut.license;
			std::string plateColor = pdjVarOut.color;
			std::cout << plateColor.c_str() << " : " << pathname.c_str() << std::endl;
			djResultout << plateColor.c_str() << " : " << pathname.c_str() << std::endl;
		}
		else
		{
			djResultout << "Fail to find plate!" << dwReturn << std::endl;
			std::cout << "Fail to find plate!" << dwReturn << std::endl;
		}
		//imshow("test", srcMat);//显示结果
		//cvWaitKey(0);// 按空格显示下一张
	}
	//---------------------------释放----------------------------//
	djResultout.close();
	LPR_UnInitEx();
	return 0;
}
