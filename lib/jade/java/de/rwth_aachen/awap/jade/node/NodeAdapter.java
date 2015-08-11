package de.rwth_aachen.awap.jade.node;

import jade.domain.DFService;
import jade.domain.FIPAException;
import jade.domain.FIPAAgentManagement.DFAgentDescription;
import jade.lang.acl.ACLMessage;

import java.util.ArrayList;

import de.rwth_aachen.awap.Property;
import de.rwth_aachen.awap.RemoteAgent;
import de.rwth_aachen.awap.ServiceClient;
import de.rwth_aachen.awap.ServiceProvider;
import de.rwth_aachen.awap.TxMessage;
import de.rwth_aachen.awap.jade.AgentRegistry;
import de.rwth_aachen.awap.jade.WrapperAgent;
import de.rwth_aachen.awap.jade.generated.Communication;
import de.rwth_aachen.awap.jade.generated.Service;
import de.rwth_aachen.awap.node.AbstractNode;


/**
 * Presents a unique Node interface for every agent.
 * @author Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 * @author Artur Loewen <aloewen@eonerc.rwth-aachen.de>
 *
 */
public class NodeAdapter extends AbstractNode{

	private Node node;
	private WrapperAgent wrapper;
	// private LocalAgent agent;
	private ArrayList<ACLMessage> subscriptionMessages = new ArrayList<ACLMessage>();

	public NodeAdapter(Node node, WrapperAgent wrapper){
		this.node = node;
		this.wrapper = wrapper;
	}

	@Override
	public void send(TxMessage tx_msg) {
		System.out.println("NodeAdapter: Agent " + this.wrapper.getName() + " called send.");
		ACLMessage msg = Communication.awapToJade(tx_msg);
		msg.setSender(this.wrapper.getAID());
		msg.addReceiver(AgentRegistry.getId(tx_msg.receiver.id));
		this.wrapper.send(msg);
	}

	@Override
	public boolean registerService(ServiceProvider service) {
		System.out.println("NodeAdapter: Agent " + this.wrapper.getName() + " called registerService.");

		DFAgentDescription dfd = new DFAgentDescription();
		dfd.setName(this.wrapper.getAID());
		try {
			dfd.addServices(Service.providerToDescription(service));
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
	public boolean deregisterService(ServiceProvider service) {
		System.out.println("NodeAdapter: Agent " + this.wrapper.getName() + " called deregisterService.");
		try {
			DFService.deregister(this.wrapper);
			return true;
		} catch (FIPAException fe) {
			fe.printStackTrace();
			return false;
		}
	}

	@Override
	public byte installServiceListener(final ServiceClient listener,
			Property... properties) {
		System.out.println("NodeAdapter: Agent " + this.wrapper.getName() + " called installServiceListener.");

		// define search parameters
		DFAgentDescription dfd = new DFAgentDescription();
		try {
			dfd.addServices(Service.clientToDescription(listener, properties));
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			return -1;
		}

		ACLMessage subscriptionMessage =
				DFService.createSubscriptionMessage(this.wrapper, this.wrapper.getDefaultDF(), dfd, null);

		this.wrapper.send(subscriptionMessage);

		// save subscription message for later cancelation
		this.subscriptionMessages.add(subscriptionMessage);
		return (byte)(this.subscriptionMessages.size() - 1);
	}

	/**
	 * Handles messages from the df.
	 * @return `true` if message was consumed
	 */
	public boolean handleDfMessage(ACLMessage msg) {
		if(msg.getSender().equals(this.wrapper.getDefaultDF())) {
			try {
				for(DFAgentDescription result : DFService.decodeNotification(msg.getContent())) {
					boolean registration = result.getAllServices().hasNext();
					RemoteAgent remoteAgent = new RemoteAgent();
					remoteAgent.id = AgentRegistry.getId(result.getName());
					// TODO: determine if service found or removed...
					if(registration) {
						System.out.println("NodeAdapter: Found new agent: " + result.getName());
						// listener.serviceFound((byte)0, remoteAgent);
					} else {
						System.out.println("NodeAdapter: Agent died: " + result.getName());
						// listener.serviceRemoved((byte)0, remoteAgent);
					}
				}
			} catch (FIPAException fe) {
				fe.printStackTrace();
			}
			return true;
		} else {
			return false;
		}
	}

	@Override
	public boolean uninstallServiceListener(byte listenerId) {
		System.out.println("NodeAdapter: Agent " + this.wrapper.getName() + " called uninstallServiceListener.");
		ACLMessage cancelMessage = DFService.createCancelMessage(
				this.wrapper, this.wrapper.getDefaultDF(), this.subscriptionMessages.get(listenerId));
		// send the message
		this.wrapper.send(cancelMessage);
		return true;
	}

}
