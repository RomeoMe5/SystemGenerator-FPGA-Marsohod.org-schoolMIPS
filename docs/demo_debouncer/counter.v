module counter (
    input wire clk_50MHz_i, // Generator
    input wire [7:0] sb_i, // Tumblers
    input wire sw_i, // Button
    output wire [7:0] led_o, // Leds
    // 7-segment indicator
    output wire [7:0] hg0_o,
    output wire [7:0] hg1_o
);
    wire sw_down;
    ButtonDebouncer debouncer (
        .clk_i(clk_50MHz_i),
        .rst_i(),
        .sw_i(sw_i),
        .sw_state_o(),
        .sw_down_o(sw_down),
        .sw_up_o()
    );

    reg [7:0] count;
    always @ (posedge sw_down) begin
        count <= count + 1;
    end

    Seven hg0 (.code_i(count[3:0]), .hg_o(hg0_o));
    Seven hg1 (.code_i(count[7:4]), .hg_o(hg1_o));

endmodule
