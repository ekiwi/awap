/**
 * GUITemperatureConsumer.java
 *
 * Copyright (c) 2016 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

package de.rwth_aachen.awap.example.agents;

import java.awt.BorderLayout;
import java.awt.Font;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;

import javax.swing.JFrame;
import javax.swing.JTextArea;

import de.rwth_aachen.awap.Agent;
import de.rwth_aachen.awap.RemoteAgent;
import de.rwth_aachen.awap.enums.Building;
import de.rwth_aachen.awap.enums.Room;
import de.rwth_aachen.awap.messages.TemperatureService.RequestTemperature;
import de.rwth_aachen.awap.messages.TemperatureService.Temperature;
import de.rwth_aachen.awap.service.remote.ITemperatureServiceClient;
import de.rwth_aachen.awap.service.remote.TemperatureService;

public class GUITemperatureConsumer extends Agent implements ITemperatureServiceClient {
	private TemperatureService.Type temperaturSensorType;

	private JTextArea textArea;
	private JFrame frame;

	private void initializeGUI() {
		frame = new JFrame("AWAP Demo - Temperature Consumer");
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		Font font = new Font("Mono", Font.BOLD, 40);
		textArea = new JTextArea(5, 20);
		textArea.setEditable(false);
		textArea.setFont(font);
		textArea.setText("Hello\nWorld");
		frame.getContentPane().add(textArea, BorderLayout.CENTER);
		frame.pack();
		frame.setVisible(true);
	}

	class Result {
		public Result(RemoteAgent sender, int value) {
			this.sender = sender;
			this.value = value;
			this.date = new Date();
		}
		public RemoteAgent sender;
		public Date date;
		public int value;
	}

	private HashMap<Integer, Result> results = new HashMap<Integer, Result>();

	private DateFormat dateFormat = new SimpleDateFormat("HH:mm:ss");

	private String resultLine(Result res) {
		return dateFormat.format(res.date) + ": from " +
				res.sender.id + ": " + res.value + "\n";
	}

	public void setup() {
		this.requestWakeUp(500, new Integer(0));
		// temperature services in Building1 in Room1
		this.temperaturSensorType = new TemperatureService.Type(
				this).building(Building.Build1).room(Room.R1);
		initializeGUI();
	}

	public void onReceive(Temperature msg) {
		Result result = new Result(msg.getRemoteAgent(), msg.value);
		results.put(result.sender.id, result);
		String text = "";
		for(Result res : this.results.values()) {
			text += resultLine(res);
		}
		this.textArea.setText(text);
	}

	public void onWakeUp(Object obj) {
		int ii = (Integer)obj;
		System.out.println("Agent: Woke up: " + ii);
		this.temperaturSensorType.send(new RequestTemperature());
		this.requestWakeUp(1000, new Integer(ii+1));
	}

}
