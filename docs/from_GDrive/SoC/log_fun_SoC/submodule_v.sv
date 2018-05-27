module sum_v(ina, inb, inp, out0, full);

	// Input Port(s)
	input ina;
	input inb;
	input inp;
	
	// Output Port(s)
	output  out0;
	output  full;
	
	wire [1:0] sum;
	
	// Additional Module Item(s)
   assign sum=ina+inb+inp;
	//assign out0=sum[0];
	//assign full=sum[1];
	assign {full,out0}=sum;

endmodule
