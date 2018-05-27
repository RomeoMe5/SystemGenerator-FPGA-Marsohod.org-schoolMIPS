module shift_register(
	clk,
	output_1,
	output_2
);
	input clk;
	output reg output_1; // latch   gpio 32
	output reg output_2; // ds gpio 34

	reg[0:7] data;
	reg transfer_data;
	integer counter;

	initial
	begin
		transfer_data = 1'b0;
		output_1 = 1'b0;
		output_2 = 1'b0;
		data = 8'b01010101;
	end

	always@(posedge clk)
	begin
		// если нет еще не начата передача данных то начинаем
		// и фиксируем этот момент
		if(transfer_data == 1'b0)
		begin
		// флога начала передачи данных
		transfer_data = 1'b1;

		//защелка latch b2 (gpio_32) в ноль
		output_2 = 1'b0;
		counter = 0;
		end

		// начинаем передачу данных
		if(transfer_data == 1'b1)
		begin
			if(counter == 7)
			begin
				output_1 = 1'b1; //защелка latch b2 (gpio_32) в единицу
				counter = 0;
				transfer_data = 1'b0;
			end else
			begin
				output_2 = data[counter];
				counter = counter+1;
			end
		end
	end

endmodule
