package de.rwth_aachen.awap;

public class Agent {
	private byte id;
	private IDomainFacilitator df;

	public Agent(byte id, IDomainFacilitator df) {
		this.id = id;
		this.df = df;
	}

	public byte getId() {
		return id;
	}
}
