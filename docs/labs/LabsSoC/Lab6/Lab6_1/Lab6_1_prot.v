module Lab6_1_prot(clk, input1, output1, clr, state);
  input clk, clr, input1;
  output output1, state;

  reg clk1;
  wire clk_lab;
  wire [3:0] state;
  reg [24:0] counter;

  initial
	begin
    counter = 25'b0;
	end

  Lab6_1_1 Lab6(clk_lab, clr, input1, output1, state);

  always@(posedge clk)
	 begin
    if(counter == 25'd25000000)
      begin
        clk1 <= 1'b1;
        counter <= 25'd0;
      end
    else
      clk1 <= 1'b0;
	 counter <= counter + 1'b1;
	 end
	 
	 assign clk_lab = clk1;

endmodule
