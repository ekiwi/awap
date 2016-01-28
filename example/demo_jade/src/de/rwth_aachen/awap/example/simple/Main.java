/**
 * Main.java
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */


package de.rwth_aachen.awap.example.simple;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.BorderFactory;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JSlider;
import javax.swing.Timer;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;

import de.rwth_aachen.awap.jade.node.Node;
import jade.core.Profile;
import jade.core.ProfileImpl;
import jade.core.Runtime;
import jade.util.ExtendedProperties;
import jade.util.leap.Properties;
import jade.wrapper.AgentController;
import jade.wrapper.ContainerController;

public class Main {

	static Node defaultNode;
	static JFrame frame;
	static JLabel sensorLabel;
	static JLabel actorLabel;
	static Timer actorPollTimer;

	static class SliderListener implements ChangeListener {
		@Override
		public void stateChanged(ChangeEvent e) {
			JSlider source = (JSlider)e.getSource();
			if (!source.getValueIsAdjusting()) {
				int value = source.getValue();
				sensorLabel.setText("" + value);
				defaultNode.sensorValue = value;
			}
		}
	}


	public static void updateActorValueDisplay(int value) {
		actorLabel.setText("" + value);
		if(value > 0) {
			actorLabel.setBackground(Color.YELLOW);
		} else {
			actorLabel.setBackground(Color.GRAY);
		}
	}
	private static void initializeGUI() {
		frame = new JFrame("AWAP Demo - Node GUI");
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		frame.setLayout(new GridLayout(2,1));
		// Sensor Value
		JPanel sensorPanel = new JPanel();
		sensorPanel.setBorder(BorderFactory.createTitledBorder("Sensor Value"));
		sensorLabel = new JLabel("0", JLabel.CENTER);
		JSlider sensorSlider = new JSlider(JSlider.HORIZONTAL, 0, 1000, 500);
		sensorSlider.addChangeListener(new SliderListener());
		sensorLabel.setText("" + sensorSlider.getValue());
		defaultNode.sensorValue = sensorSlider.getValue();
		sensorPanel.add(sensorLabel);
		sensorPanel.add(sensorSlider);
		frame.add(sensorPanel);
		// Actor Value
		JPanel actorPanel = new JPanel();
		actorPanel.setBorder(BorderFactory.createTitledBorder("Actor Value"));
		actorLabel = new JLabel("", JLabel.CENTER);
		Dimension size = new Dimension(300,150);
		actorLabel.setSize(size);
		actorLabel.setMinimumSize(size);
		actorLabel.setPreferredSize(size);
		actorLabel.setOpaque(true);
		updateActorValueDisplay(defaultNode.actorValue);
		actorPanel.add(actorLabel);
		frame.add(actorPanel);
		frame.pack();
		frame.setVisible(true);
		// start actor poll timer
		actorPollTimer = new Timer(100, new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e){
				updateActorValueDisplay(defaultNode.actorValue);
			}
		});
		actorPollTimer.setInitialDelay(200);
		actorPollTimer.start();
	}

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
		defaultNode = new Node("DemoNode0");

		// initialize GUI for node
		initializeGUI();

		AgentController temperatureAgent0 = defaultNode.createNewAgent(cc, "TemperatureAgent0", "de.rwth_aachen.awap.example.agents.TemperatureSensor");
		temperatureAgent0.start();
		AgentController temperatureConsumer0 = defaultNode.createNewAgent(cc, "GUITemperatureConsumer0", "de.rwth_aachen.awap.example.agents.GUITemperatureConsumer");
		temperatureConsumer0.start();

		//Thread.sleep(2000);
		//temperatureAgent0.kill();

		//Thread.sleep(2000);
		//temperatureConsumer0.kill();

	}
}
