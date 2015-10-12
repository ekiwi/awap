/**
 * NodeAdapter.java
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

package de.rwth_aachen.awap.mote;

import de.rwth_aachen.awap.BroadcastMessage;
import de.rwth_aachen.awap.Message;
import de.rwth_aachen.awap.ServiceDescription;
import de.rwth_aachen.awap.AbstractNode;
import de.rwth_aachen.awap.Agent;

public class NodeAdapter extends AbstractNode {
	static void initializeAgent(Agent agent, int agentId) {
		NodeAdapter adapter = new NodeAdapter();
		adapter.agentId = agentId;
		agent.init(agentId, adapter);
	}

	public int agentId;
	public native void send(Message msg);
	public native void send(BroadcastMessage msg);
	public native void requestWakeUp(int milliseconds, byte index);
	public native boolean deregisterService(int localServiceId);
	public native boolean registerService(int localServiceId, ServiceDescription description);
}
