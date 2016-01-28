/**
 * Main.java
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */


package de.rwth_aachen.awap.example.simple;

import de.rwth_aachen.awap.jade.node.Node;
import jade.core.Profile;
import jade.core.ProfileImpl;
import jade.core.Runtime;
import jade.util.ExtendedProperties;
import jade.util.leap.Properties;
import jade.wrapper.AgentController;
import jade.wrapper.ContainerController;

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
		Node subscriberNode= new Node("ConsumerNode0");

		AgentController temperatureAgent0 = temperatureNode.createNewAgent(cc, "TemperatureAgent0", "de.rwth_aachen.awap.example.agents.TemperatureSensor");
		temperatureAgent0.start();
		AgentController temperatureConsumer0 = subscriberNode.createNewAgent(cc, "GUITemperatureConsumer0", "de.rwth_aachen.awap.example.agents.GUITemperatureConsumer");
		temperatureConsumer0.start();

		//Thread.sleep(2000);
		//temperatureAgent0.kill();

		//Thread.sleep(2000);
		//temperatureConsumer0.kill();

	}
}
