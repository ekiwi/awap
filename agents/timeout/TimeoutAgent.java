package de.rwth_aachen.awap.agents;

import de.rwth_aachen.awap.Agent;
import de.rwth_aachen.awap.Node;

public class TimeoutAgent implements Agent{

	public TimeoutAgent(String name, Node node) {
		
		this.name = name;
		this.node = agent;
		this.node.registerTimeout(this, 1000);
		this.node.registerTimeout(this, 2000);
	}

	public void handleEvent(Event event) {
		if(event instanceof TimeoutEvent) {
			int deltaTimeMs = ((TimeoutEvent)event).deltaTimeMs;
			System.out.println(this.name + ": Timeout called after " + deltaTimeMs + " ms.");
		}
	}

}
