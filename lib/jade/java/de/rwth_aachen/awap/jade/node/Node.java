/**
 * Node.java
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

package de.rwth_aachen.awap.jade.node;

import java.util.Stack;

import de.rwth_aachen.awap.jade.WrapperAgent;
import jade.wrapper.AgentController;
import jade.wrapper.ContainerController;
import jade.wrapper.StaleProxyException;

/**
 * This class simulates a Node for JADE Agents.
 *
 * @author Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 */
public class Node {
	private static int nodeCounter = 0;
	private String name;
	private Stack<Integer> ids = new Stack<Integer>();;
	private int address;
	//private LocalAgent[] agents;

	public int sensorValue;
	public int actorValue;

	public Node(String name) {
		this.address = nodeCounter;
		nodeCounter++;
		for(int ii = 0; ii < 8; ++ii){
			this.ids.push(ii);
		}
		//this.agents = new LocalAgent[this.ids.size()];
		this.name = name;
	}

	public String getName() {
		return this.name;
	}

	public AgentController createNewAgent(ContainerController cc, String agent_name, String agent_class) throws StaleProxyException {
		// tell JADE to construct a wrapper for the newly created agent
		Object[] args = { this, agent_class, this.ids.pop() };
		return cc.createNewAgent(agent_name, WrapperAgent.class.getName(), args);
	}

	public void deregisterAgent(int id) {
		this.ids.push(id);
	}
}
