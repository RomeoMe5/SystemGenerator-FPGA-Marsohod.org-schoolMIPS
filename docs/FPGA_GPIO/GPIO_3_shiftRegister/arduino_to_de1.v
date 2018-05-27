module arduino_to_de1(
	clk,
	b1,
	b2,
	b3,
	output_led1,
	output_led2,
	output_led3
);
	input clk;
	input b1;
	input b2;
	input b3;
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
		output_led1 = b1;
		output_led2 = b2;
		output_led3 = b3;
	end

endmodule
