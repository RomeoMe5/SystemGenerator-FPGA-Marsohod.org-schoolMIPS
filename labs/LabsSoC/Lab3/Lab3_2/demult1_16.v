module demult1_16(D, A0, A1, A2, A3, Q0, Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10, Q11, Q12, Q13, Q14, Q15);

input wire	D, A0, A1, A2, A3;
output wire	Q0, Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10, Q11, Q12, Q13, Q14, Q15;

wire	dm_1_1_Q0, dm_1_1_Q1;
wire	dm_2_1_Q0, dm_2_1_Q1, dm_2_2_Q0, dm_2_2_Q1;
wire	dm_3_1_Q0, dm_3_1_Q1, dm_3_2_Q0, dm_3_2_Q1, dm_3_3_Q0, dm_3_3_Q1, dm_3_4_Q0, dm_3_4_Q1;

wire	dm_4_1_Q0, dm_4_1_Q1, dm_4_2_Q0, dm_4_2_Q1, dm_4_3_Q0, dm_4_3_Q1, dm_4_4_Q0, dm_4_4_Q1;
wire	dm_4_5_Q0, dm_4_5_Q1, dm_4_6_Q0, dm_4_6_Q1, dm_4_7_Q0, dm_4_7_Q1, dm_4_8_Q0, dm_4_8_Q1;

demult1_2 demult_1_1(.D(D),.A(A3),.Q0(dm_1_1_Q0),.Q1(dm_1_1_Q1));

demult1_2 demult_2_1(.D(dm_1_1_Q0),.A(A2),.Q0(dm_2_1_Q0),.Q1(dm_2_1_Q1));
demult1_2 demult_2_2(.D(dm_1_1_Q1),.A(A2),.Q0(dm_2_2_Q0),.Q1(dm_2_2_Q1));

demult1_2 demult_3_1(.D(dm_2_1_Q0),.A(A1),.Q0(dm_3_1_Q0),.Q1(dm_3_1_Q1));
demult1_2 demult_3_2(.D(dm_2_1_Q1),.A(A1),.Q0(dm_3_2_Q0),.Q1(dm_3_2_Q1));
demult1_2 demult_3_3(.D(dm_2_2_Q0),.A(A1),.Q0(dm_3_3_Q0),.Q1(dm_3_3_Q1));
demult1_2 demult_3_4(.D(dm_2_2_Q1),.A(A1),.Q0(dm_3_4_Q0),.Q1(dm_3_4_Q1));

demult1_2 demult_4_1(.D(dm_3_1_Q0),.A(A0),.Q0(dm_4_1_Q0),.Q1(dm_4_1_Q1));
demult1_2 demult_4_2(.D(dm_3_1_Q1),.A(A0),.Q0(dm_4_2_Q0),.Q1(dm_4_2_Q1));
demult1_2 demult_4_3(.D(dm_3_2_Q0),.A(A0),.Q0(dm_4_3_Q0),.Q1(dm_4_3_Q1));
demult1_2 demult_4_4(.D(dm_3_2_Q1),.A(A0),.Q0(dm_4_4_Q0),.Q1(dm_4_4_Q1));
demult1_2 demult_4_5(.D(dm_3_3_Q0),.A(A0),.Q0(dm_4_5_Q0),.Q1(dm_4_5_Q1));
demult1_2 demult_4_6(.D(dm_3_3_Q1),.A(A0),.Q0(dm_4_6_Q0),.Q1(dm_4_6_Q1));
demult1_2 demult_4_7(.D(dm_3_4_Q0),.A(A0),.Q0(dm_4_7_Q0),.Q1(dm_4_7_Q1));
demult1_2 demult_4_8(.D(dm_3_4_Q1),.A(A0),.Q0(dm_4_8_Q0),.Q1(dm_4_8_Q1));

assign	Q0 = dm_4_1_Q0;
assign	Q1 = dm_4_1_Q1;
assign	Q2 = dm_4_2_Q0;
assign	Q3 = dm_4_2_Q1;
assign	Q4 = dm_4_3_Q0;
assign	Q5 = dm_4_3_Q1;
assign	Q6 = dm_4_4_Q0;
assign	Q7 = dm_4_4_Q1;
assign	Q8 = dm_4_5_Q0;
assign	Q9 = dm_4_5_Q1;
assign	Q10 = dm_4_6_Q0;
assign	Q11 = dm_4_6_Q1;
assign	Q12 = dm_4_7_Q0;
assign	Q13 = dm_4_7_Q1;
assign	Q14 = dm_4_8_Q0;
assign	Q15 = dm_4_8_Q1;

endmodule
