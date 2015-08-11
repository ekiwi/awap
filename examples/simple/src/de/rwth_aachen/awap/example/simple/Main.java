package de.rwth_aachen.awap.example.simple;

import jade.core.Profile;
import jade.core.ProfileImpl;
import jade.core.Runtime;
import jade.lang.acl.ACLMessage;
import jade.util.ExtendedProperties;
import jade.util.leap.Properties;
import jade.wrapper.AgentController;
import jade.wrapper.ContainerController;
import de.rwth_aachen.awap.RemoteAgent;
import de.rwth_aachen.awap.jade.generated.Communication;
import de.rwth_aachen.awap.jade.node.Node;
import de.rwth_aachen.awap.service.TemperatureServiceClient;
import de.rwth_aachen.awap.service.TemperatureServiceProvider;

public class Main {

	public static void main(String[] args) throws Exception {
		// Get a hold on JADE runtime
		final Runtime rt = Runtime.instance();

		// Shut JVM down, when agent runtime closes
		rt.setCloseVM(true);

		// activate RMA GUI
		Properties prop = new ExtendedProperties();
		prop.setProperty(Profile.GUI, "false");

		// Create a default profile
		Profile p = new ProfileImpl(prop);

		// Create a new main container with profile
		final ContainerController cc = rt.createMainContainer(p);

		// create temperature node and agent
		Node temperatureNode= new Node("TemperatureNode0");
		Node subscriberNode= new Node("SubscriberNode0");

		AgentController temperatureAgent0 = temperatureNode.createNewAgent(cc, "TemperatureAgent0", "de.rwth_aachen.awap.example.agents.TemperatureSensor");
		temperatureAgent0.start();
		AgentController temperatureSubscriber0 = subscriberNode.createNewAgent(cc, "SimpleTemperatureSubscriber0", "de.rwth_aachen.awap.example.agents.SimpleTemperatureSubscriber");
		temperatureSubscriber0.start();


		Thread.sleep(2000);
		temperatureAgent0.kill();

		Thread.sleep(2000);
		temperatureSubscriber0.kill();

	}

	private static void testCommunicationConversion() throws Exception{
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
		System.out.println("Packet: "+ (Communication.jadeToAwap(jade_msg)).getClass().getName());
	}

}
