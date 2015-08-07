package de.rwth_aachen.awap.example.simple;

import jade.lang.acl.ACLMessage;
import de.rwth_aachen.awap.RemoteAgent;
import de.rwth_aachen.awap.jade.generated.Communication;
import de.rwth_aachen.awap.service.TemperatureServiceClient;
import de.rwth_aachen.awap.service.TemperatureServiceProvider;

public class Main {

	public static void main(String[] args) throws Exception {
		System.out.println("Hello World!");

		RemoteAgent smith = new RemoteAgent();
		smith.id = 1337;
		short value = (short)9001;
		TemperatureServiceProvider.Temperature tx
		= new TemperatureServiceProvider.Temperature(smith, value);
		System.out.println("Temperature before converting back from JADE: "+ tx.value);


		ACLMessage jade_msg = Communication.awapToJade(tx);

		System.out.println(jade_msg);

		TemperatureServiceClient.Temperature rx = (TemperatureServiceClient.Temperature)Communication.jadeToAwap(jade_msg);
		System.out.println("Temperature after converting back from JADE: "+ rx.value);
	}

}
