package de.rwth_aachen.awap.agents;

import de.rwth_aachen.awap.Agent;
import de.rwth_aachen.awap.EventHandler;

public class TimeoutAgent implements EventHandler{
	private String name;
	private Agent agent;

	public TimeoutAgent(String name, Agent agent) {
		this.name = name;
		this.agent = agent;
		this.agent.registerTimeout(this, 1000);
		this.agent.registerTimeout(this, 2000);
	}

	public void handleEvent(Event event) {
		if(event instanceof TimeoutEvent) {
			int deltaTimeMs = ((TimeoutEvent)event).deltaTimeMs;
			System.out.println(Agent.this.name + ": Timeout called after " + deltaTimeMs + " ms.");
		}
	}

}
