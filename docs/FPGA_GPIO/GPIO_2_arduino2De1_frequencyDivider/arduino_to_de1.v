module arduino_to_de1(
    clk,
    input_b1,
    input_b2,
    input_b3,
    output_led1,
    output_led2,
    output_led3
);
    input clk;
    input input_b1;
    input input_b2;
    input input_b3;
    output reg output_led1;
    output reg output_led2;
    output reg output_led3;

    initial
    begin
        output_led1 = 1'b0;
        output_led2 = 1'b0;
        output_led3 = 1'b0;
    end

    always@(posedge clk)
    begin
        output_led1 = input_b1;
        output_led2 = input_b2;
        output_led3 = input_b3;
    end

endmodule
