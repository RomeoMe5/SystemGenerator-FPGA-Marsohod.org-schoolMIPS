module demult1_8(EN, D, A0, A1, A2, Q0, Q1, Q2, Q3, Q4, Q5, Q6, Q7);

input wire	EN, D, A0, A1, A2;
output wire	Q0, Q1, Q2, Q3, Q4, Q5, Q6, Q7;

wire	EN_inv;

wire	dm_1_1_Q0;
wire	dm_1_1_Q1;

wire	dm_2_1_Q0;
wire	dm_2_1_Q1;
wire	dm_2_2_Q0;
wire	dm_2_2_Q1;

wire	dm_3_1_Q0;
wire	dm_3_1_Q1;
wire	dm_3_2_Q0;
wire	dm_3_2_Q1;
wire	dm_3_3_Q0;
wire	dm_3_3_Q1;
wire	dm_3_4_Q0;
wire	dm_3_4_Q1;

demult1_2 demult_1_1(.D(D),.A(A2),.Q0(dm_1_1_Q0),.Q1(dm_1_1_Q1));

demult1_2 demult_2_1(.D(dm_1_1_Q0),.A(A1),.Q0(dm_2_1_Q0),.Q1(dm_2_1_Q1));
demult1_2 demult_2_2(.D(dm_1_1_Q1),.A(A1),.Q0(dm_2_2_Q0),.Q1(dm_2_2_Q1));

demult1_2 demult_3_1(.D(dm_2_1_Q0),.A(A0),.Q0(dm_3_1_Q0),.Q1(dm_3_1_Q1));
demult1_2 demult_3_2(.D(dm_2_1_Q1),.A(A0),.Q0(dm_3_2_Q0),.Q1(dm_3_2_Q1));
demult1_2 demult_3_3(.D(dm_2_2_Q0),.A(A0),.Q0(dm_3_3_Q0),.Q1(dm_3_3_Q1));
demult1_2 demult_3_4(.D(dm_2_2_Q1),.A(A0),.Q0(dm_3_4_Q0),.Q1(dm_3_4_Q1));

assign	EN_inv = ~EN;

assign	Q0 = EN_inv & dm_3_1_Q0;
assign	Q1 = EN_inv & dm_3_1_Q1;
assign	Q2 = EN_inv & dm_3_2_Q0;
assign	Q3 = EN_inv & dm_3_2_Q1;
assign	Q4 = EN_inv & dm_3_3_Q0;
assign	Q5 = EN_inv & dm_3_3_Q1;
assign	Q6 = EN_inv & dm_3_4_Q0;
assign	Q7 = EN_inv & dm_3_4_Q1;


endmodule