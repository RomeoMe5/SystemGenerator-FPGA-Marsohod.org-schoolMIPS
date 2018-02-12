module digit16_to_7segm(Q0, Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10, Q11, Q12, Q13, Q14, Q15, 
			S0, S1, S2, S3, S4, S5, S6, dp);

input wire	Q0, Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10, Q11, Q12, Q13, Q14, Q15;
output wire	S0, S1, S2, S3, S4, S5, S6, dp;

assign	S0 = ~(Q0 | Q2 | Q3 | Q5 | Q6 | Q7 | Q8 | Q9 | Q10 | Q11 | Q12 | Q13 | Q14 | Q15);
assign	S1 = ~(Q0 | Q1 | Q2 | Q3 | Q4 | Q7 | Q8 | Q9 | Q10 | Q11 | Q13);
assign	S2 = ~(Q0 | Q1 | Q3 | Q4 | Q5 | Q6 | Q7 | Q8 | Q9 | Q10 | Q11 | Q13);
assign	S3 = ~(Q0 | Q2 | Q3 | Q5 | Q6 | Q8 | Q9 | Q11 | Q12 | Q13 | Q14);
assign	S4 = ~(Q0 | Q2 | Q6 | Q8 | Q10 | Q11 | Q12 | Q13 | Q14 | Q15);
assign	S5 = ~(Q0 | Q4 | Q5 | Q6 | Q8 | Q9 | Q10 | Q11 | Q12 | Q13 | Q14 | Q15);
assign	S6 = ~(Q2 | Q3 | Q4 | Q5 | Q6 | Q8 | Q9 | Q10 | Q11 | Q14 | Q15);
assign	dp = ~(Q0 | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 | Q8 | Q9);

endmodule
