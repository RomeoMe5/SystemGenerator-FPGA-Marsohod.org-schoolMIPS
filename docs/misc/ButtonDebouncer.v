/*
 * Eliminates mechanical button bouncing.
 */
module ButtonDebouncer  #(
    parameter CNT_WIDTH = 10
)(
    input clk_i, rst_i, sw_i,
    output reg sw_state_o, sw_down_o, sw_up_o
);
    // Sync input with current clock domain
    reg [1:0] sw_r;
    always @(posedge rst_i or posedge clk_i) begin
        if (rst_i) begin
            sw_r <= 2'b00;
        end else begin
            sw_r <= { sw_r[0], ~sw_i };
        end
    end

    reg [CNT_WIDTH-1:0] sw_count;
    wire sw_change_f = (sw_state_o != sw_r[1]);
    wire sw_cnt_max = &sw_count;
    always @(posedge rst_i or posedge clk_i) begin
        if (rst_i) begin
            sw_count <= 0;
            sw_state_o <= 0;
        end else if (sw_change_f) begin
            sw_count <= sw_count + 1;
            if (sw_cnt_max) begin
                sw_state_o <= ~sw_state_o;
            end
        end else begin
            sw_count <= 0;
        end
    end

    always @(posedge clk_i) begin
        sw_down_o <= sw_change_f & sw_cnt_max & ~sw_state_o;
        sw_up_o <= sw_change_f & sw_cnt_max & sw_state_o;
    end

endmodule
