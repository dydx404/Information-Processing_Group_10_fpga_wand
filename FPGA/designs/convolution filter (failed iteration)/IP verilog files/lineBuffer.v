`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03/30/2020 07:25:49 PM
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
    parameter I_WIDTH = 1280
)(
input   i_clk,
input   i_rst,
input [7:0] i_data,
input   i_data_valid,
output [23:0] o_data,
input i_rd_data
);


localparam PTR_WIDTH = $clog2(I_WIDTH);

reg [7:0] line [I_WIDTH-1:0]; //line buffer
reg [PTR_WIDTH-1:0] wrPntr;
reg [PTR_WIDTH-1:0] rdPntr;

initial $display("PTR_WIDTH = %d", PTR_WIDTH);

always @(posedge i_clk)
begin
    if(i_data_valid)
        line[wrPntr] <= i_data;
end

always @(posedge i_clk)
begin
    if(i_rst)
        wrPntr <= 'd0;
    else if(i_data_valid)
        begin
            if(wrPntr == (I_WIDTH-1))
                wrPntr <= 'd0;
            else
                wrPntr <= wrPntr + 'd1;
                
        end
end
wire [PTR_WIDTH-1:0] rdPntr1 = (rdPntr + 1 >= I_WIDTH) ? rdPntr     : rdPntr + 1;
wire [PTR_WIDTH-1:0] rdPntr2 = (rdPntr + 2 >= I_WIDTH) ? I_WIDTH - 1 : rdPntr + 2;
always@(*)
begin
    if(rdPntr >= I_WIDTH)
        $display("rdPntr overflow"); 
    if(rdPntr1 >= I_WIDTH)
        $display("rdPntr1 overflow"); 
    if(rdPntr2 >= I_WIDTH)
        $display("rdPntr2 overflow"); 
end
assign o_data = {line[rdPntr],line[rdPntr1],line[rdPntr2]};

always @(posedge i_clk)
begin
    if(i_rst)
        rdPntr <= 'd0;
    else if(i_rd_data)
        begin
            if(rdPntr == (I_WIDTH-1))
                rdPntr <= 'd0;
            else
                rdPntr <= rdPntr + 'd1;
            // $display("rdPntr = %d", rdPntr);
            
                
        end
        
        
end


endmodule