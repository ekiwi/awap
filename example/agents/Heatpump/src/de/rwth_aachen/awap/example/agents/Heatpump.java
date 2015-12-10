/**
 * TemperatureSensor.java
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

package de.rwth_aachen.awap.example.agents;

import de.rwth_aachen.awap.Agent;
import de.rwth_aachen.awap.enums.Building;
import de.rwth_aachen.awap.enums.Room;
import de.rwth_aachen.awap.enums.SupplyCircuit;
import de.rwth_aachen.awap.enums.TemperatureAction;
import de.rwth_aachen.awap.messages.EnergySupplyService.AcceptProposal;
import de.rwth_aachen.awap.messages.EnergySupplyService.ProposeAction;
import de.rwth_aachen.awap.messages.EnergySupplyService.RefuseAction;
import de.rwth_aachen.awap.messages.EnergySupplyService.RejectProposal;
import de.rwth_aachen.awap.messages.EnergySupplyService.RequestProposal;



public class Heatpump extends Agent {
	final short ST_WAITING_FOR_CFP = 0;
	final short ST_WAITING_FOR_PROPOSAL_REPLY = 1;
			
	EnergySupplyService localService;
	
	boolean isOn = true;
	boolean canIncrease = true;
	boolean canDecrease = true;
	boolean isHeating = true;
	boolean isCooling = false;

	int resetCounter = 0;

	public void setup(){
		// initialize services
		this.localService = new EnergySupplyService();
	}

	public void onWakeUp(Object obj) {
		int ii = (Integer)obj;
		// if the reset counter has not been increased
		if(ii == resetCounter) {
			this.localService.state = ST_WAITING_FOR_CFP;
			resetCounter++;
		}
	}

	private class EnergySupplyService extends de.rwth_aachen.awap.service.local.EnergySupplyService {
		public short state = ST_WAITING_FOR_CFP;
		public EnergySupplyService() {
			super(Heatpump.this, Building.Build1, SupplyCircuit.SC1, Room.R1);
		}

		public void onReceive(RequestProposal msg) {
			boolean propose = false;
			if(msg.action == TemperatureAction.Decrease) {
				propose = (isHeating && canDecrease) || (isCooling && canIncrease);
			} else if(msg.action == TemperatureAction.Increase) {
				propose = (isHeating && canIncrease) || (isCooling && canDecrease);
			}
			if(state == ST_WAITING_FOR_CFP && propose && isOn) {
				// it's all free
				int posGradCost = 0;
				int negGradCost = 0;
				this.send(msg.getRemoteAgent(), new ProposeAction(
						isOn, canIncrease, canDecrease,
						isHeating, isCooling,
						posGradCost, negGradCost));
				state = ST_WAITING_FOR_PROPOSAL_REPLY;
				Heatpump.this.requestWakeUp(2000, new Integer(resetCounter));
			} else {
				this.send(msg.getRemoteAgent(), new RefuseAction());
			}
		}

		public void onReceive(AcceptProposal msg) {
			if(state == ST_WAITING_FOR_PROPOSAL_REPLY) {
				// TODO: send command to heat pump
				resetCounter++;
				state = ST_WAITING_FOR_CFP;
			}
		}

		public void onReceive(RejectProposal msg) {
			// do nothing
		}
	}
}
