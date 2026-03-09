`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 02/22/2026 04:17:39 PM
// Design Name: 
// Module Name: lineBuffer
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


module lineBuffer#(
    parameter IMAGE_WIDTH = 1080, 
              RBG = 0
)(
    input i_clk,
    input i_rst, 
    input i_data_valid, 
    input[7:0] i_data, 
    output[23:0] o_data,  
    input i_rd_data
    );

reg [7:0] line [511:0]; //line buffer
reg [8:0] rdPtr; // assumes width is 512 = 2^8
reg [8:0] wrPtr; 

always@(posedge i_clk)
begin 
    if(i_data_valid)
        line[wrPtr] <= i_data; 
end

always@(posedge i_clk)
begin 
    if(i_rst)
        wrPtr <= 'd0;
    else if(i_data_valid)
        wrPtr <= wrPtr + 'd1; 
end

assign o_data = {line[rdPtr],line[rdPtr+1],line[rdPtr+2]}; 

always@(posedge i_clk)
begin
    if(i_rst)
        rdPtr <= 'd0; 
    else if (i_rd_data)
        rdPtr <= rdPtr + 'd1; 
end


endmodule
