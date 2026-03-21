`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 04/01/2020 08:10:25 PM
// Design Name: 
// Module Name: imageProcessTop
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


module imageProcessTop#( 
    parameter I_WIDTH = 1280, 
              I_HEIGHT = 720
)(
input   axi_clk,
input   axi_reset_n,
//slave interface
input   i_data_valid,
input [7:0] i_data,
output  o_data_ready,
//master interface
output  o_data_valid,
output [7:0] o_data,
input   i_data_ready,
//interrupt
output  o_intr,
output   tlast,
output reg [$clog2(I_WIDTH*I_HEIGHT)-1:0] tlastCounter

    );
    


wire [71:0] pixel_data;
wire pixel_data_valid;
wire axis_prog_full;
wire [7:0] convolved_data;
wire convolved_data_valid;

assign o_data_ready = !axis_prog_full;
    
imageControl #(
    .I_WIDTH(I_WIDTH),
    .I_HEIGHT(I_HEIGHT)
)IC(
    .i_clk(axi_clk),
    .i_rst(!axi_reset_n),
    .i_pixel_data(i_data),
    .i_pixel_data_valid(i_data_valid),
    .o_pixel_data(pixel_data),
    .o_pixel_data_valid(pixel_data_valid),
    .o_intr(o_intr)
  );    
  
 conv conv(
     .i_clk(axi_clk),
     .i_pixel_data(pixel_data),
     .i_pixel_data_valid(pixel_data_valid),
     .o_convolved_data(convolved_data),
     .o_convolved_data_valid(convolved_data_valid)
 ); 
 
 outputBuffer OB (
   .wr_rst_busy(),        // output wire wr_rst_busy
   .rd_rst_busy(),        // output wire rd_rst_busy
   .s_aclk(axi_clk),                  // input wire s_aclk
   .s_aresetn(axi_reset_n),            // input wire s_aresetn
   .s_axis_tvalid(convolved_data_valid),    // input wire s_axis_tvalid
   .s_axis_tready(),    // output wire s_axis_tready
   .s_axis_tdata(convolved_data),      // input wire [7 : 0] s_axis_tdata
   .m_axis_tvalid(o_data_valid),    // output wire m_axis_tvalid
   .m_axis_tready(i_data_ready),    // input wire m_axis_tready
   .m_axis_tdata(o_data),      // output wire [7 : 0] m_axis_tdata
   .axis_prog_full(axis_prog_full)  // output wire axis_prog_full
 );
 
 localparam ALL_WIDTH = $clog2(I_WIDTH*I_HEIGHT); 
 localparam IMG_SIZE = I_WIDTH*I_HEIGHT; 
 
 initial begin
    // transactCounter = 0; 
 end

 always @(posedge axi_clk) begin
     if(!axi_reset_n) begin
        tlastCounter <= 0; 
     end else begin
        if(tlastCounter == (20'hE0600-1)) begin
                tlastCounter <= 0;
            end else begin
                if(o_data_valid && i_data_ready) begin
                    tlastCounter <= tlastCounter + 1; 
                end
                // $display("tlastCounter %d", tlastCounter); 
            end
        
     end
 end

assign tlast = (tlastCounter == 20'hE0600-1); 
 /*
  always @(posedge axi_clk) begin
     if(!axi_reset_n) begin
        transactCounter <= 0; 
     end else begin
        if(o_data_ready && i_data_valid) begin
            transactCounter <= transactCounter + 1; 
        end
     end
 end
 */
  
    
    
endmodule