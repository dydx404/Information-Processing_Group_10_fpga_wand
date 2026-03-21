`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 04/02/2020 08:11:41 PM
// Design Name: 
// Module Name: tb
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////

`define headerSize 1080

module tb#(
    parameter I_WIDTH = 1280, 
              I_HEIGHT = 720
)(

    );
function integer clog2;
    input integer value;
          integer temp;
    begin
        temp = value - 1;
        for (clog2 = 0; temp > 0; clog2 = clog2 + 1) begin
            temp = temp >> 1;
        end
    end
endfunction  

localparam imageSize = I_WIDTH*I_HEIGHT; 
 
 reg clk;
 reg reset;
 reg [7:0] imgData;
 integer file,file1,i;
 reg imgDataValid;
 integer sentSize;
 wire[10:0] check;
 wire intr;
 wire [7:0] outData;
 wire outDataValid;
 integer receivedData=0;
 wire tlast; 
 wire [19:0] tlastCounter; 
 wire o_data_ready;
 // wire [$clog2(I_WIDTH*I_HEIGHT)-1:0] transactCounter;  

 initial
 begin
    clk = 1'b0;
    forever
    begin
        #5 clk = ~clk;
    end
 end
 
 initial
 begin
    reset = 0;
    sentSize = 0;
    imgDataValid = 0;
    #100;
    reset = 1;
    #100;
    file = $fopen("test.bmp","rb");
    file1 = $fopen("hello_world.bmp","wb");
    for(i=0;i<`headerSize;i=i+1)
    begin
        $fscanf(file,"%c",imgData);
        $fwrite(file1,"%c",imgData);
    end
    
    for(i=0;i<4*I_WIDTH;i=i+1)
    begin
        @(posedge clk);
        $fscanf(file,"%c",imgData);
        imgDataValid <= 1'b1;
    end
    sentSize = 4*I_WIDTH;
    @(posedge clk);
    imgDataValid <= 1'b0;
    while(sentSize < imageSize)
    begin
        @(posedge intr);
        for(i=0;i<I_WIDTH;i=i+1)
        begin
            @(posedge clk);
            $fscanf(file,"%c",imgData);
            imgDataValid <= 1'b1;    
        end
        @(posedge clk);
        imgDataValid <= 1'b0;
        sentSize = sentSize+I_WIDTH;
    end
    @(posedge clk);
    imgDataValid <= 1'b0;
    @(posedge intr);
    for(i=0;i<I_WIDTH;i=i+1)
    begin
        @(posedge clk);
        imgData <= 0;
        imgDataValid <= 1'b1;    
    end
    @(posedge clk);
    imgDataValid <= 1'b0;
    @(posedge intr);
    for(i=0;i<I_WIDTH;i=i+1)
    begin
        @(posedge clk);
        imgData <= 0;
        imgDataValid <= 1'b1;    
    end
    @(posedge clk);
    imgDataValid <= 1'b0;
    $fclose(file);
 end
 
 always @(posedge clk)
 begin
     if(outDataValid)
     begin
         $fwrite(file1,"%c",outData);
         receivedData = receivedData+1;
     end 
     if(receivedData == imageSize)
     begin
        $fclose(file1);
        $stop;
     end
 end
 
 imageProcessTop #(
    .I_WIDTH(I_WIDTH), 
    .I_HEIGHT(I_HEIGHT)
 ) dut(
    .axi_clk(clk),
    .axi_reset_n(reset),
    //slave interface
    .i_data_valid(imgDataValid),
    .i_data(imgData),
    .o_data_ready(o_data_ready),
    //master interface
    .o_data_valid(outDataValid),
    .o_data(outData),
    .i_data_ready(1'b1),
    //interrupt
    .o_intr(intr), 
    .tlast(tlast), 
    .tlastCounter(tlastCounter)
    // .transactCounter(transactCounter)
);   

assign check = clog2(512); 
    
endmodule