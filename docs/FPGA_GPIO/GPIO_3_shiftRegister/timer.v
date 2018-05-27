module timer(
		input_clk,
		reset,
		start_elapse,
		stop_elapse,
		out_H_min,
		out_L_min,
		out_H_sec,
		out_L_sec,
		out_sign
);
	input input_clk;
	input reset;
	input start_elapse;
	input stop_elapse;
	output reg[4:0]out_H_min;
	output reg[4:0]out_L_min;
	output reg[4:0]out_H_sec;
	output reg[4:0]out_L_sec;
	output reg[4:0]out_sign;
		
	reg[4:0] H_min;
	reg[4:0] L_min;
	reg[4:0] H_sec;
	reg[4:0] L_sec;
	reg[4:0] sign;
	reg end_time;
	reg stoped_elapse;
	
	initial
	begin
		stoped_elapse = 1'b0;
		end_time = 1'b0;
		//H_min = 5'b00010;		//20 минут 00 секунд
		H_min = 5'b00000;
		//L_min = 5'b00000;
		L_min = 5'b00001;
		H_sec = 5'b00000;
		L_sec = 5'b00000;
		sign =  5'b11111; // выключен
	end
	
	always@(posedge input_clk)
	begin
		if(reset)
		begin
			stoped_elapse = 1'b0;
			end_time = 1'b0;
			H_min = 5'b00010;		//20 минут 00 секунд
			L_min = 5'b00000;
			H_sec = 5'b00000;
			L_sec = 5'b00000;
		end
		if(stop_elapse)
		begin
			stoped_elapse = 1'b1;
		end

		if(start_elapse && !stoped_elapse)
		begin
			if(!end_time)
			begin
				sign = 5'b11111;
				if(L_sec > 5'b00000) // если в единицах секун не 0
				begin
					L_sec = L_sec - 1'b1;
				end
				else begin // если в единицах секунд 0, то надо занять у дксятков секунд
					if(H_sec > 5'b00000) // если в десятках секунд не 0 то занимаем в единицы и вычитаем из десятков
					begin
						H_sec = H_sec - 1'b1;
						L_sec = 5'b01001;
					end
					else begin // если в десятках секун 0 то занимаем у минут
						if(L_min > 5'b00000)
						begin
							L_min = L_min - 1'b1;
							H_sec = 5'b00101;
							L_sec = 5'b01001;
						end
						else begin
							if(H_min > 5'b00000)
							begin
								H_min = H_min - 1'b1;
								L_min = 5'b01001;
								H_sec = 5'b00101;
								L_sec = 5'b01001;
							end
							else begin // если в старшем 0 минут то и в остальных 0 значит время закончилось
								end_time = 1'b1;
								out_sign = 5'b10001;
							end
						end
					end
				end
			end
			else begin
				sign = 5'b10001;
				if(L_sec < 5'b01001)
				begin
					L_sec = L_sec + 1'b1;
				end
				else begin
					if(H_sec < 5'b00101)
					begin
						L_sec = 5'b00000;
						H_sec = H_sec + 1'b1;
					end
					else begin
						if(L_min < 5'b01001)
						begin
							L_sec = 5'b00000;
							H_sec = 5'b00000;
							L_min = L_min + 1'b1;
						end
						else begin
							L_sec = 5'b00000;
							H_sec = 5'b00000;
							L_min = 5'b00000;
							H_min = H_min + 1'b1;
						end
					end
				end
			end
		end
		out_H_min = H_min;
		out_L_min = L_min;
		out_H_sec = H_sec;
		out_L_sec = L_sec;
		out_sign = sign;
		
	end

endmodule
