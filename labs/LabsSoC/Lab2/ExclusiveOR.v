module ExclusiveOR(x1,x2,f);
       input  x1,x2;
       output  f;
       assign f = ( x1 &  ~x2 )|( ~x1 & x2 );
endmodule

