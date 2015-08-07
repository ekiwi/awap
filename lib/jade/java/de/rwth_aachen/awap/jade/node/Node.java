package de.rwth_aachen.awap.jade.node;

import de.rwth_aachen.awap.Property;
import de.rwth_aachen.awap.ServiceClient;
import de.rwth_aachen.awap.ServiceProvider;
import de.rwth_aachen.awap.TxMessage;
import de.rwth_aachen.awap.node.AbstractNode;

/**
 * This class simulates a Node for JADE Agents.
 *
 * @author Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 */
public class Node extends AbstractNode{
	private String name;

	public Node(String name) {
		this.name = name;
	}

	@Override
	public void send(TxMessage msg) {
		System.out.println("Node " + this.name + " wants to send a message");
	}

	@Override
	public boolean registerService(ServiceProvider service) {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public boolean deregisterService(ServiceProvider service) {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public byte installServiceListener(ServiceClient listener,
			byte serviceType, Property... properties) {
		// TODO Auto-generated method stub
		return 0;
	}

	@Override
	public boolean uninstallServiceListener(byte listenerId) {
		// TODO Auto-generated method stub
		return false;
	}
}
