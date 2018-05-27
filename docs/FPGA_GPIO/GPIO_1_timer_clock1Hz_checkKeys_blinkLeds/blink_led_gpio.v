module blink_led_gpio(
    clk,
    gpio_0_35
);

    input clk;
    output reg gpio_0_35;
    reg turn;

    initial
    begin
        turn = 1'b0;
    end

    always @(posedge clk)
    begin
        turn = turn + 1'b1;
        gpio_0_35 = turn;
    end

endmodule
