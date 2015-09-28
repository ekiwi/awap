/**
 * NodeAdapter.java
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

package de.rwth_aachen.awap.mote;

import java.util.ArrayList;
import de.rwth_aachen.awap.BroadcastMessage;
import de.rwth_aachen.awap.LocalService;
import de.rwth_aachen.awap.Message;
import de.rwth_aachen.awap.AbstractNode;
import de.rwth_aachen.awap.Agent;

public class NodeAdapter extends AbstractNode {
	static void initializeAgent(Agent agent, int agentId) {
		NodeAdapter adapter = new NodeAdapter();
		adapter.agentId = agentId;
		adapter.owner = agent;
		agent.init(agentId, adapter);
	}

	public int agentId;
	private Agent owner;
	private ArrayList<Object> callbackObjects = new ArrayList<Object>();

	public void onWakeUp(short index) {
		// retrieve object
		Object obj = callbackObjects.get(index);
		callbackObjects.set(index, null);
		// call agent
		this.owner.onWakeUp(obj);
	}

	public void requestWakeUp(int milliseconds, Object obj) {
		// put obj into array list
		// check if there are empty spots
		for(short ii = 0; ii < callbackObjects.size(); ++ii) {
			if(callbackObjects.get(ii) == null) {
				callbackObjects.set(ii, obj);
				requestWakeUpWithIndex(milliseconds, ii);
				return;
			}
		}
		// if not insert at the end
		callbackObjects.add(obj);
		requestWakeUpWithIndex(milliseconds, (short)(callbackObjects.size()-1));
	}

	public native void send(Message msg);
	public native void send(BroadcastMessage msg);
	public native void requestWakeUpWithIndex(int milliseconds, short index);
	public native boolean deregisterService(LocalService service);
	public native boolean registerService(LocalService service);
}
