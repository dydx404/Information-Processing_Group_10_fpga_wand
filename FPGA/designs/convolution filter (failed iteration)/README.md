# FPGA Convolution Filter (Failed Iteration)
#### Ackowledgement
This hardware iteration is a failed version in prior to the centroid IP. <br>
Due to that I am a beginner in FPGA design, I followed very closely to Vipin Kizheppatt course on FPGA design. The design is mainly his design, with some very minor changes on (1) image size (2) handshake protocol. <br>
Link: https://www.youtube.com/playlist?list=PLXHMvqUANAFOviU0J8HSp0E91lLJInzX1 <br>

#### Introduction
The hardware responsibility is to accept input video stream, do appropriate processing, and return a set of coordinations of blob centroid(s) back to processing system. The "proposed" function flow: (double quotation on "proposed" because I didnt actually finish them)<br>
\[Input video stream\] -> \[Pixel downsampling\] -> \[Convolution filter/noise elimination\] -> \[Image to logical map conversion\] -> \[Centroid calculation \] -> \[Output stream\]

#### Path layout
This path contains three folders: <br>
- Hardware files
- Simulation files
- IP files.


#### Hardware layout
<img width="1463" height="615" alt="image" src="https://github.com/user-attachments/assets/bad5cb35-3d2d-4135-a177-ea0ce6a41a42" />
The 
