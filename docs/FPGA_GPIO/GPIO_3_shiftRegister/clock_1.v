module clock_1(
	input_clk,
	output_clk
);
	input input_clk;
	output reg output_clk;
	
	reg signal;
	reg[5:0] counter;
	reg[5:0] const_data = 6'b001100;
	
	initial
	begin
		signal = 1'b0;
		counter = 6'b0;
	end

	always@(posedge input_clk)
	begin
		counter = counter + 1'b1;
		if(counter == const_data)
		begin
			signal = ~signal;
			counter = 6'b0;
		end
			output_clk = signal;
	end

endmodule
