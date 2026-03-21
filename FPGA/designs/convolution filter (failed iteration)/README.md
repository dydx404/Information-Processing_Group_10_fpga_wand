# FPGA Convolution Filter (Failed Iteration)
#### Ackowledgement
This hardware iteration is a failed version in prior to the centroid IP. <br>
Due to that I am a beginner in FPGA design, I followed very closely to Vipin Kizheppatt course on FPGA design. The design is mainly his design, with some very minor changes on (1) image size (2) handshake protocol. <br>
Link: https://www.youtube.com/playlist?list=PLXHMvqUANAFOviU0J8HSp0E91lLJInzX1 <br>

#### Introduction
The hardware responsibility is to accept input video stream, do appropriate processing, and return a set of coordinations of blob centroid(s) back to processing system. The "proposed" function flow: (double quotation on "proposed" because I didnt actually finish them)<br>
**\[Input video stream\] -> \[Pixel downsampling\] -> \[Convolution filter/noise elimination\] -> \[Image to logical map conversion\] -> \[Centroid calculation \] -> \[Output stream\]** <br>
Below explain more detailedly on each part responsibility: <br>
- **Input stream:** The video input specification is (1280 \* 720 \* 3) dimension, coloured image. The camera used is Arducam, with OpenCV as driver to capture video. Notice the processing loop is from input video stream to output stream, hence in order to achieve real-time processing, the requirement of timing between two ends must be able to achieve, 24 fps(self-defined goal). 
- **Pixel downsamping:** Transform the shape of frame from (1280, 720, 3) to (640, 360, 1) for faster processing speed. This is done by typical video downsampling technique, which is only sample N-th bit in video file. From a RGB format to greyscale image, the typical formula has 0.299 \* R + 0.587 \* G + 0.114 \* B, we use an approximation 0.3\*R + 0.6\*G + 0.15\*B to achieve the RGB to gray conversion. Note that, due to we only want to find the intensity of the light source instead of the colour, gray scale is more ideal for processing power.
- **Convolution filter:** Used for cleaning up the high frequency (salt/pepper) noise from the surrounding. Refer to Vipin Kizheppatt course, the idea is to have, with a N x N size kernel, having (N+1) line buffer to load the image row pixels, alternatively switch between load mode and store mode, for which, when N line buffers are operating (outputing pixel in that row) the other one loads a new row of pixel from DDR (via DMA). And multiplexers to input different combination of rows into the kernel, then output to a output buffer for the next stage.
-  **Image to logical map:** This stage simply observe the pixel intensity, compare to a set threshold and output to 0 or 1. The main purpose is to transform (640 \* 360) bytes to (640 \* 360) bits for faster / more compact stream
-  **Centroid calculation:** Using the logical map correspond to the location, a centroid can be calculated. Depending on the noise of the surrounding, a second stage of convolution filter is optional to add into the pipeline before this.
-  **Output stream:** The information send back to processing unit will be the (x, y) coordinate of the blob. For simplicity we assume there is only one light source for now, and in order to prevent other light source, we have (1) IR camera filter (2) arducam has inbuilt light exposure automatic adjustment for the brightest source.


#### Path layout
This path contains three folders: <br>
- Hardware files
- Simulation files
- IP files.


#### Hardware layout
<img width="1463" height="615" alt="image" src="https://github.com/user-attachments/assets/bad5cb35-3d2d-4135-a177-ea0ce6a41a42" />
A confession: this is only partial design of the above pipeline. The only custom IP made is convolution filter, the following paragraph, when refer to IP, will be referred to convolution filter IP. <br>
The function flow here is: <br>
**\[Input stream\] -> \[Convolution filter (custom IP)\] -> \[Output stream\]** <br>
With DMA interconnection for faster transferal between PS -> IP and IP -> PS. <br>

#### 


#### Simulation
In the simulation folder it contains a test image (of my handsome face), output result and a testbench verilog file. The level of simulation is IP-level (DUT is the convolution filter IP). The convolution kernel used in simulation is edge detection, as a proof of concept, even though in the project function flow the required kernel type is Gaussian noise filter. However changing the kernel type is fairly fast and easy compare to other parts of the design. <br>
As can be seen, the IP successfully achieve the edge detection, with correct size specification. 

#### Issue encountered
The main issue encounter in this hardware iteration is mainly in <br>
`dma_recvchannel.wait()` <br>

Using ILA, it was found that the transfered bytes and received bytes are not the same. The required transfer bytes are 1280 \* 720, while the receieved bytes are 1280 \* 718, with last two rows missing. The reason is still remain unknown, but I suspected it may due to one of the following reasons: <br>

- TLAST assertion: (however checking from ILA, TLAST is indeed asserted and the timing is correct in simulation, and confirmed there is no potential deadlock from the upstream signals)
- Boundary condition of convolution filter IP: perhaps the last two rows in line buffer is not output.

#### Lesson learnt
In terms of the hardware / technical side, I have learnt a lot in the following aspect:

- ILA and hardware manager, waveform viewing and debug
- AXI-stream protocol and handshake 
- RTL design (including race condition, signal timing, blocking & non-blocking assignment)
- Simulation and testbench (tb in verilog instead of C++)

In terms of project / soft-skill wise, due to the mentioned issue above, I have spent 2-3 weeks on solving this issue, resulting a significant delay in the project. While learning RTL from scratch is an essential skill, I should prioritise on the project deadline and quickly shift to alternative solution / work around it. This time the project timeline is significantly delayed due to me (Wells)
