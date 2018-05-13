module mac
(
    input[7:0] Ain, Bin,
    output[15:0] Pout
);
    wire[7:0] S_wire, A_wire, B_wire;
    wire Cout, Cin;

    assign B_wire = Ain*Bin[1];
    assign A_wire = Ain*Bin[0];
    my_sum summ1(.Ain(A_wire), .Bin(B_wire), .Ci(Cin), .Sout(S_wire), .Co(Cout));

endmodule

module my_sum (Ain, Bin, Ci, Sout, Co);
    input Ain, Bin, Ci;
    output Sout, Co;
    
    wire [7:0] Ain, Bin, Sout, C;
    wire Ci, Co;

    bitsum sum1(Ain[0], Bin[0], Sout[0], Ci, C[0]);
    bitsum sum2(Ain[1], Bin[1], Sout[1], C[0], C[1]);    
    bitsum sum3(Ain[2], Bin[2], Sout[2], C[1], C[2]);
    bitsum sum4(Ain[3], Bin[3], Sout[3], C[2], C[3]);
    bitsum sum5(Ain[4], Bin[4], Sout[4], C[3], C[4]);
    bitsum sum6(Ain[5], Bin[5], Sout[5], C[4], C[5]);
    bitsum sum7(Ain[6], Bin[6], Sout[6], C[5], C[6]);
    bitsum sum8(Ain[7], Bin[7], Sout[7], C[6], C[7]);

    assign Co = C[7];

endmodule
 
module bitsum (A, B, Cin, S, Cout);
    input A, B, Cin;
    output S, Cout;
    
    wire A, B, S, Res;
    wire c1, c2, Cin, Cout;
        
    xor(Res, A, B);
    and(c1, A, B);
    xor(S, Cin, Res);
    and(c2, Cin, Res);
    or(Cout, c1, c2);

endmodule
