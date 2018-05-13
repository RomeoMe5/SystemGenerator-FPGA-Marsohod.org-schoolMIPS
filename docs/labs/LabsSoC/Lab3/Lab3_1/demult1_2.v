module demult1_2(A,D,Q0,Q1);

input wire	A, D;
output wire	Q0, Q1;

assign	Q0 = D & ~A;
assign	Q1 = D & A;

endmodule
