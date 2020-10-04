import cv2
import numpy as np

class VideoStream():
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        # self.tracker = cv2.TrackerCSRT_create()
    
    def __del__(self):
        self.cap.release()


    def get_frame(self):
        def stackImages(imgArray,scale,lables=[]):
            rows = len(imgArray)
            cols = len(imgArray[0])
            rowsAvailable = isinstance(imgArray[0], list)
            width = imgArray[0][0].shape[1]
            height = imgArray[0][0].shape[0]
            if rowsAvailable:
                for x in range ( 0, rows):
                    for y in range(0, cols):
                        imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                        if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
                imageBlank = np.zeros((height, width, 3), np.uint8)
                hor = [imageBlank]*rows
                hor_con = [imageBlank]*rows
                for x in range(0, rows):
                    hor[x] = np.hstack(imgArray[x])
                    hor_con[x] = np.concatenate(imgArray[x])
                ver = np.vstack(hor)
                ver_con = np.concatenate(hor)
            else:
                for x in range(0, rows):
                    imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
                    if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
                hor= np.hstack(imgArray)
                hor_con= np.concatenate(imgArray)
                ver = hor
            if len(lables) != 0:
                eachImgWidth= int(ver.shape[1] / cols)
                eachImgHeight = int(ver.shape[0] / rows)
                #print(eachImgHeight)
                for d in range(0, rows):
                    for c in range (0,cols):
                        cv2.rectangle(ver,(c*eachImgWidth,eachImgHeight*d),(c*eachImgWidth+len(lables[d][c])*13+27,30+eachImgHeight*d),(255,255,255),cv2.FILLED)
                        cv2.putText(ver,lables[d][c],(eachImgWidth*c+10,eachImgHeight*d+20),cv2.FONT_HERSHEY_COMPLEX,0.7,(255,0,255),2)
            return ver
        def rectContours(contours):
            rectCon = []
            for i in contours:
                area = cv2.contourArea(i)
                perimeter = cv2.arcLength(i,True) # True means closed
                approx = cv2.approxPolyDP(i,0.02*perimeter,True)
                # print(approx) # Corner Points
                # print(len(approx)) # No. of corners
                if len(approx) == 4:
                    rectCon.append(i)
            rectCon = sorted(rectCon,key = cv2.contourArea,reverse =True)
            return rectCon        
        def getCornerPoints(contour):
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour,True) 
            approx = cv2.approxPolyDP(contour,0.02*perimeter,True)
            return approx
        def reorderMyPoints(myPoints):
            myPoints = myPoints.reshape((4,2))
            myPointsnew = np.zeros((4,1,2),np.int32)
            add = myPoints.sum(1) # axis = 1 -> Along the row.
            myPointsnew[0] = myPoints[np.argmin(add)]  # [0,0]
            myPointsnew[3] = myPoints[np.argmax(add)]  # [w,h]
            diff = np.diff(myPoints,axis=1) # y-x
            myPointsnew[1] = myPoints[np.argmin(diff)] # [w,0]
            myPointsnew[2] = myPoints[np.argmax(diff)] # [0,h]
            return myPointsnew        
        def splitBoxes(img):
            rows = np.vsplit(img,5)
            boxes = []
            for r in rows:
                col = np.hsplit(r,5)
                for c in col:
                    boxes.append(c)
                    return boxes        
        def showAnswers(img,myIndex,grading,ans,question,choices):
            secW = int(img.shape[1]//choices)
            secH = int(img.shape[0]//question)
            for i in range(question):
                myAns = myIndex[i]
                cX = (myAns*secW) + secW//2
                cY = (i*secH) + secH//2
                if(grading[i]==1):
                    myColor = (0,255,0)
                else:
                    myColor = (0,0,255)
                    corAns = ans[i]
                    cv2.circle(img,((corAns*secW)+secW//2,cY),20,(0,255,0),cv2.FILLED)
                cv2.circle(img,(cX,cY),50,myColor,cv2.FILLED)
            return img            
        
        path = "Data/1.jpg"
        widthImg = 700
        heightImg = 700
        question = 5
        choices = 5
        ans = [1,2,0,1,4]
        webCamFeed = True

        if webCamFeed:success, img = self.cap.read()
        else:img = cv2.imread(pathImage)



        img=cv2.resize(img,(widthImg,heightImg))
        imgContours = img.copy()
        imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray,(5,5),1)   # (5,5) -> Kernel
        imgFinalContours = img.copy()
        imgInvWarpColored = np.zeros_like(img)
        imgFinal = img.copy()
        # imgTest = img.copy()


        try:
            # Detecting Edges
            imgCanny = cv2.Canny(imgBlur,10,50) # 10,50 - >Threshhold
            contours , hierarchy = cv2.findContours(imgCanny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
            cv2.drawContours(imgContours,contours,-1,(0,255,0),10)# -1 -> To draw all contours
            imgBlank = np.zeros_like(img)


            # Detecting Rectangles
            rectCon = rectContours(contours)
            '''biggestContour = rectCon[0]''' # Here we are getting a lot of points
            biggestContour = getCornerPoints(rectCon[0])
            gradePoints = getCornerPoints(rectCon[1])
            # print(gradePoints)
            if biggestContour.size!=0 and gradePoints.size!=0:
                cv2.drawContours(imgFinalContours,biggestContour,-1,(0,255,0),20)
                cv2.drawContours(imgFinalContours,gradePoints,-1,(255,0,0),20)


                biggestContour = reorderMyPoints(biggestContour)
                pt1 = np.float32(biggestContour)
                pt2 = np.float32([[0,0],[widthImg,0],[0,heightImg],[widthImg,heightImg]])
 
                matrix = cv2.getPerspectiveTransform(pt1,pt2)
                imgWarpColored = cv2.warpPerspective(img,matrix,(widthImg,heightImg))


                gradePoints = reorderMyPoints(gradePoints)
                pt1g = np.float32(gradePoints)
                pt2g = np.float32([[0,0],[325,0],[0,150],[325,150]])
                matrixg = cv2.getPerspectiveTransform(pt1g,pt2g)
                imgGradeDisplayColored = cv2.warpPerspective(img,matrixg,(325,150))

                imgWarpGray = cv2.cvtColor(imgWarpColored,cv2.COLOR_BGR2GRAY)
                imgThresh = cv2.threshold(imgWarpGray,170,255,cv2.THRESH_BINARY_INV)[1] # ->We can change 150,255 as per our need, 255 is max value.
                boxes = splitBoxes(imgThresh)


                countR=0
                countC=0
                myPixelVal = np.zeros((question,choices)) 


                # TO STORE THE NON ZERO VALUES OF EACH BOX

                for image in boxes:
                    #cv2.imshow(str(countR)+str(countC),image)
                    totalPixels = cv2.countNonZero(image)
                    myPixelVal[countR][countC]= totalPixels
                    countC += 1
                    if (countC==choices):countC=0;countR +=1


                myIndex = []
                for i in range(question):
                    arr = myPixelVal[i]
                    myIndexval = np.where(arr == np.amax(arr))
                    # print(myIndexval)
                    myIndex.append(myIndexval[0][0])
                # print(myIndex)    

                gradings = []
                for i in range(question):
                    if ans[i]==myIndex[i]:
                        gradings.append(1)
                    else:
                        gradings.append(0)
                score = (sum(gradings)/question)*100

                img_1 =imgWarpColored.copy()
                imgRawDrawing = np.zeros_like(imgWarpColored)
                imgResult = showAnswers(img_1,myIndex,gradings,ans,question,choices)
                imgRawDrawing = showAnswers(imgRawDrawing,myIndex,gradings,ans,question,choices)



                invMatrix = cv2.getPerspectiveTransform(pt2,pt1)
                imgInvWarpColored = cv2.warpPerspective(imgRawDrawing,invMatrix,(widthImg,heightImg))


                imgRawDisplay = np.zeros_like(imgGradeDisplayColored)
                cv2.putText(imgRawDisplay,str(int(score))+"%",(70,100),cv2.FONT_HERSHEY_COMPLEX,3,(0,255,255),3)
                matrixgInv = cv2.getPerspectiveTransform(pt2g,pt1g)
                imgGradeDisplayColoredInv = cv2.warpPerspective(imgRawDisplay,matrixgInv,(widthImg,heightImg))    






                imgFinal = cv2.addWeighted(imgFinal,1,imgInvWarpColored,1,0)
                imgFinal = cv2.addWeighted(imgFinal,1,imgGradeDisplayColoredInv,1,0)
                ret, jpeg = cv2.imencode('.jpeg', imgFinal)
                    # Stacking Images
                imgArray = ([img,imgGray,imgBlur,imgCanny],[imgContours,imgFinalContours,imgWarpColored,imgThresh],
                    [imgResult,imgRawDrawing,imgInvWarpColored,imgGradeDisplayColoredInv],
                   [imgFinal,imgBlank,imgBlank,imgBlank])

        except:
            imgArray = ([imgBlank,imgBlank,imgBlank,imgBlank],[imgBlank,imgBlank,imgBlank,imgBlank],
                        [imgBlank,imgBlank,imgBlank,imgBlank],[imgBlank,imgBlank,imgBlank,imgBlank])

        return jpeg.tobytes()