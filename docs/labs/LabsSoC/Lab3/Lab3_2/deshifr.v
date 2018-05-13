module deshifr(A0, A1, A2, A3, Q0, Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10, Q11, Q12, Q13, Q14, Q15);

input wire	A0, A1, A2, A3;
output wire	Q0, Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10, Q11, Q12, Q13, Q14, Q15;

assign	Q15 = A3 & A2 & A1 & A0;
assign	Q14 = A3 & A2 & A1 & ~A0;
assign	Q13 = A3 & A2 & ~A1 & A0;
assign	Q12 = A3 & A2 & ~A1 & ~A0;
assign	Q11 = A3 & ~A2 & A1 & A0;
assign	Q10 = A3 & ~A2 & A1 & ~A0;
assign	Q9 = A3 & ~A2 & ~A1 & A0;
assign	Q8 = A3 & ~A2 & ~A1 & ~A0;
assign	Q7 = ~A3 & A2 & A1 & A0;
assign	Q6 = ~A3 & A2 & A1 & ~A0;
assign	Q5 = ~A3 & A2 & ~A1 & A0;
assign	Q4 = ~A3 & A2 & ~A1 & ~A0;
assign	Q3 = ~A3 & ~A2 & A1 & A0;
assign	Q2 = ~A3 & ~A2 & A1 & ~A0;
assign	Q1 = ~A3 & ~A2 & ~A1 & A0;
assign	Q0 = ~A3 & ~A2 & ~A1 & ~A0;

endmodule
