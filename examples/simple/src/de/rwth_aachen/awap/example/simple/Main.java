package de.rwth_aachen.awap.example.simple;

import jade.lang.acl.ACLMessage;
import de.rwth_aachen.awap.RemoteAgent;
import de.rwth_aachen.awap.jade.generated.Communication;
import de.rwth_aachen.awap.service.TemperatureServiceProvider;

public class Main {

	public static void main(String[] args) {
		System.out.println("Hello World!");

		RemoteAgent smith = new RemoteAgent();
		smith.id = 1337;
		short value = (short)9001;
		TemperatureServiceProvider.Temperature msg
		= new TemperatureServiceProvider.Temperature(smith, value);

		ACLMessage jade_msg = Communication.awapToJade(msg);

		System.out.println(jade_msg);
	}

}
