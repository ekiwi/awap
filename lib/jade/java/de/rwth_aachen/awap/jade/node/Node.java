/**
 * Node.java
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

package de.rwth_aachen.awap.jade.node;

import jade.wrapper.AgentController;
import jade.wrapper.ContainerController;
import jade.wrapper.StaleProxyException;

import java.util.Stack;

import de.rwth_aachen.awap.jade.WrapperAgent;

/**
 * This class simulates a Node for JADE Agents.
 *
 * @author Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 */
public class Node {
	private static int nodeCounter = 0;
	private String name;
	private Stack<Byte> ids;
	private int address;
	//private LocalAgent[] agents;

	public Node(String name) {
		this.address = nodeCounter;
		nodeCounter++;
		this.ids = new Stack<Byte>();
		for(byte ii = 0; ii < 8; ++ii){
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

	public void deregisterAgent(byte id) {
		this.ids.push(id);
	}
}
