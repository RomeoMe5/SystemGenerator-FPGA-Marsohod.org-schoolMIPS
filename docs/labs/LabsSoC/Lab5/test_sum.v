module test_sum;   // Top Level Testbench
wire Ci,cm,cr;
wire [3:0] Ain, Bin;
reg [3:0] Ain_r, Bin_r;
reg Ci_r;
wire [3:0] res_my, res_ref;

my_sum      my_block (Ain, Bin, Ci,res_my, cm);
ref_sum  ref_block (Ain, Bin, Ci, res_ref, cr);  

initial 
begin
   $display("\t\t	      Time	    Ain  Bin  Ci  res_my  cm  res_ref  cr");
   $monitor($time,,,,,Ain,,,,,Bin,,,,,Ci,,,,,res_my,,,,,,,,cm,,,,,,,res_ref,,,,,,,cr);
   #400  $finish;   
end

initial
begin
Ain_r = 1;
#50 Ain_r = 5;
#50 Ain_r = 1;
#50 Ain_r = 5;
#50 Ain_r = 1;
#50 Ain_r = 5;
#50 Ain_r = 1;
#50 Ain_r = 5;
end

initial
begin
Bin_r = 2;
#100 Bin_r = 10;
#100 Bin_r = 2;
#100 Bin_r = 10;
end

initial
begin
Ci_r = 1'b0;
#200 Ci_r = 1'b1;
end

assign Ain = Ain_r;
assign Bin = Bin_r;
assign Ci = Ci_r;


endmodule
