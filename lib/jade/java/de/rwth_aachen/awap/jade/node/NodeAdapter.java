/**
 * NodeAdapter.java
 *
 * Copyright (c) 2015 Artur Loewen <aloewen@eonerc.rwth-aachen.de>
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */


package de.rwth_aachen.awap.jade.node;

import de.rwth_aachen.awap.AbstractNode;
import de.rwth_aachen.awap.BroadcastMessage;
import de.rwth_aachen.awap.LocalService;
import de.rwth_aachen.awap.Message;
import de.rwth_aachen.awap.ServiceProperty;
import de.rwth_aachen.awap.jade.AgentRegistry;
import de.rwth_aachen.awap.jade.WrapperAgent;
import de.rwth_aachen.awap.jade.generated.Communication;
import de.rwth_aachen.awap.jade.generated.Service;
import jade.domain.DFService;
import jade.domain.FIPAException;
import jade.domain.FIPAAgentManagement.DFAgentDescription;
import jade.domain.FIPAAgentManagement.ServiceDescription;
import jade.lang.acl.ACLMessage;


/**
 * Presents a unique Node interface for every agent.
 * @author Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 * @author Artur Loewen <aloewen@eonerc.rwth-aachen.de>
 *
 */
public class NodeAdapter extends AbstractNode {

	private Node node;
	private WrapperAgent wrapper;

	public NodeAdapter(Node node, WrapperAgent wrapper){
		this.node = node;
		this.wrapper = wrapper;
	}

	@Override
	public void send(Message tx_msg) {
		//System.out.println("NodeAdapter: Agent " + this.wrapper.getName() + " called send.");
		try {
			ACLMessage msg = Communication.awapToJade(tx_msg);
			msg.setSender(this.wrapper.getAID());
			msg.addReceiver(AgentRegistry.getId(tx_msg.remoteAgent.id));
			this.wrapper.send(msg);
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	@Override
	public void send(BroadcastMessage msg) {
		try {
			// 1.) find services that match description
			DFAgentDescription dfd = new DFAgentDescription();
			ServiceDescription sd = new ServiceDescription();
			sd.setType(Service.typeIdToString(msg.recipients.serviceId));
			for(ServiceProperty prop : msg.recipients.properties) {
				sd.addProperties(Service.toJadeProperty(msg.recipients.serviceId, prop));
			}
			dfd.addServices(sd);
			DFAgentDescription[] services = DFService.search(this.wrapper, this.wrapper.getDefaultDF(), dfd);

			// send message to each service
			ACLMessage jadeMsg = Communication.awapToJade(msg.msg);
			jadeMsg.setSender(this.wrapper.getAID());
			for(DFAgentDescription service : services) {
				jadeMsg.addReceiver(service.getName());
			}
			this.wrapper.send(jadeMsg);
		} catch(Exception e) {
			e.printStackTrace();
		}
	}

	@Override
	public boolean registerService(LocalService service) {
		//System.out.println("NodeAdapter: Agent " + this.wrapper.getName() + " called registerService.");

		DFAgentDescription dfd = new DFAgentDescription();
		dfd.setName(this.wrapper.getAID());
		try {
			dfd.addServices(Service.serviceToDescription(service));
		} catch(Exception e) {
			e.printStackTrace();
			return false;
		}

		try {
			DFService.register(this.wrapper, dfd);
			return true;
		} catch (FIPAException fe) {
			fe.printStackTrace();
			return false;
		}
	}

	@Override
	public boolean deregisterService(LocalService service) {
		//System.out.println("NodeAdapter: Agent " + this.wrapper.getName() + " called deregisterService.");
		try {
			DFService.deregister(this.wrapper);
			return true;
		} catch (FIPAException fe) {
			fe.printStackTrace();
			return false;
		}
	}

	@Override
	public void requestWakeUp(int milliseconds, Object obj) {
		this.wrapper.addTimeout(milliseconds, obj);
	}


}
