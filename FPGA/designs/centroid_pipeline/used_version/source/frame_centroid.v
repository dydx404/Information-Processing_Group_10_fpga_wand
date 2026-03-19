module frame_centroid #(
    parameter integer WIDTH     = 640,
    parameter integer HEIGHT    = 480,
    parameter integer THRESHOLD = 200
)(
    input  wire        axi_clk,
    input  wire        axi_reset_n,

    // AXI4-Stream slave input, 32-bit packed pixels (4 grayscale pixels/beat)
    input  wire [31:0] s_axis_tdata,
    input  wire        s_axis_tvalid,
    output wire        s_axis_tready,
    input  wire        s_axis_tlast,

    // Latched frame statistics output
    output reg  [39:0] o_sum_x,
    output reg  [39:0] o_sum_y,
    output reg  [31:0] o_count,
    output reg  [31:0] o_frame_id,
    output reg         o_valid
);

    localparam integer TOTAL_PIXELS = WIDTH * HEIGHT;

    reg [15:0] x;
    reg [15:0] y;
    reg [31:0] pixel_count;

    reg [31:0] bright_count;
    reg [39:0] sum_x;
    reg [39:0] sum_y;

    wire [7:0]  p0, p1, p2, p3;
    wire [15:0] x0, x1, x2, x3;

    wire [2:0]  bright_inc;
    wire [39:0] sum_x_inc;
    wire [39:0] sum_y_inc;

    wire [31:0] bright_total;
    wire [39:0] sum_x_total;
    wire [39:0] sum_y_total;
    wire        frame_done;

    assign s_axis_tready = 1'b1;

    // Unpack 4 grayscale pixels from each 32-bit AXI stream beat
    assign p0 = s_axis_tdata[7:0];
    assign p1 = s_axis_tdata[15:8];
    assign p2 = s_axis_tdata[23:16];
    assign p3 = s_axis_tdata[31:24];

    // Corresponding x-coordinates for the 4 pixels in this beat
    assign x0 = x;
    assign x1 = x + 16'd1;
    assign x2 = x + 16'd2;
    assign x3 = x + 16'd3;

    // Number of bright pixels in this beat
    assign bright_inc =
        (p0 >= THRESHOLD) +
        (p1 >= THRESHOLD) +
        (p2 >= THRESHOLD) +
        (p3 >= THRESHOLD);

    // Sum of x coordinates for bright pixels in this beat
    assign sum_x_inc =
        ((p0 >= THRESHOLD) ? {{24{1'b0}}, x0} : 40'd0) +
        ((p1 >= THRESHOLD) ? {{24{1'b0}}, x1} : 40'd0) +
        ((p2 >= THRESHOLD) ? {{24{1'b0}}, x2} : 40'd0) +
        ((p3 >= THRESHOLD) ? {{24{1'b0}}, x3} : 40'd0);

    // Sum of y coordinates for bright pixels in this beat
    assign sum_y_inc =
        ((p0 >= THRESHOLD) ? {{24{1'b0}}, y} : 40'd0) +
        ((p1 >= THRESHOLD) ? {{24{1'b0}}, y} : 40'd0) +
        ((p2 >= THRESHOLD) ? {{24{1'b0}}, y} : 40'd0) +
        ((p3 >= THRESHOLD) ? {{24{1'b0}}, y} : 40'd0);

    assign bright_total = bright_count + bright_inc;
    assign sum_x_total  = sum_x + sum_x_inc;
    assign sum_y_total  = sum_y + sum_y_inc;

    // End of frame either by TLAST or by expected total pixel count
    assign frame_done = s_axis_tlast || (pixel_count + 32'd4 >= TOTAL_PIXELS);

    always @(posedge axi_clk) begin
        if (!axi_reset_n) begin
            x            <= 16'd0;
            y            <= 16'd0;
            pixel_count  <= 32'd0;
            bright_count <= 32'd0;
            sum_x        <= 40'd0;
            sum_y        <= 40'd0;

            o_sum_x      <= 40'd0;
            o_sum_y      <= 40'd0;
            o_count      <= 32'd0;
            o_frame_id   <= 32'd0;
            o_valid      <= 1'b0;
        end else begin
            if (s_axis_tvalid && s_axis_tready) begin
                // Accumulate current beat into running totals
                bright_count <= bright_total;
                sum_x        <= sum_x_total;
                sum_y        <= sum_y_total;
                pixel_count  <= pixel_count + 32'd4;

                // Advance image coordinates by 4 pixels per beat
                if (x + 16'd4 >= WIDTH) begin
                    x <= 16'd0;
                    y <= y + 16'd1;
                end else begin
                    x <= x + 16'd4;
                end

                // Latch frame results and reset accumulators for next frame
                if (frame_done) begin
                    o_sum_x    <= sum_x_total;
                    o_sum_y    <= sum_y_total;
                    o_count    <= bright_total;
                    o_frame_id <= o_frame_id + 32'd1;
                    o_valid    <= 1'b1;

                    x            <= 16'd0;
                    y            <= 16'd0;
                    pixel_count  <= 32'd0;
                    bright_count <= 32'd0;
                    sum_x        <= 40'd0;
                    sum_y        <= 40'd0;
                end
            end
        end
    end

endmodule