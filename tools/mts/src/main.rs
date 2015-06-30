#![feature(lookup_host)]
#![feature(convert)]
#![feature(ip_addr)]

extern crate getopts;
extern crate regex;
use getopts::Options;
use std::env;
use std::net;
use std::net::TcpStream;
use std::io::Write;
use regex::Regex;

fn print_usage(program: &str, opts: Options) {
	let brief = format!("Usage: {} [options]", program);
	print!("{}", opts.usage(&brief));
}

fn main() {
	let args: Vec<String> = env::args().collect();
	let program = args[0].clone();

	let mut opts = Options::new();
	opts.optopt("m", "mts", "the http address of the FIPA MTS", "MTS");
	opts.optflag("h", "help", "print this help menu");

	let matches = match opts.parse(&args[1..]) {
		Ok(m) => { m }
		Err(f) => { panic!(f.to_string()) }
	};

	if matches.opt_present("h") {
		print_usage(&program, opts);
		return;
	}

	let mts_url = match matches.opt_str("m") {
		Some(x) => { x },
		None    => { println!("Error: FIPA MTS http address is required"); return }
	};

	println!("Trying to connect to {}", mts_url);

	// parse mtp address
	// e.g. "http://ip2-127.halifax.rwth-aachen.de:7778/acc"
	//      => "ip2-127.halifax.rwth-aachen.de", 7778, "/acc"
	let re = Regex::new(
		r"^(http://)?(?P<hostname>[_0-9a-zA-Z\.-]+):(?P<port>\d+)(?P<dir>[/0-9a-zA-Z]+)$"
			).unwrap();
	let caps = re.captures(mts_url.as_str()).unwrap();
	// parse address
	let hostname = caps.name("hostname").unwrap_or("");
	let port     = caps.name("port").unwrap_or("0").parse::<u16>().unwrap_or(0);
	let dir      = caps.name("dir").unwrap_or("");
	// use first possible ip
	let mut addr = net::lookup_host(hostname).unwrap().next().unwrap().unwrap();

	let mut stream = TcpStream::connect((addr.ip(), port)).unwrap();

	stream.write(b"POST ");
	stream.write(mts_url.as_bytes());
	stream.write(b" HTTP/1.1\n");
	stream.write(b"Host: ip2-127.halifax.rwth-aachen.de:7778\n");
	stream.write(b"Connection: close\n");
	stream.write(b"Content-Type: multipart-mixed ; boundary=------------------------3704d2727f559d54\n");



//> User-Agent: curl/7.40.0
//> Host: ip2-127.halifax.rwth-aachen.de:7778
//> Accept: */*
//> Connection: close
//> Content-Length: 587
//> Expect: 100-continue


//This is not part of the MIME multipart encoded message.

//--251D738450A171593A1583EB

//Content-Type: application/fipa.mts.env.rep.xml.std

//POST http://foo.com:80/acc HTTP/1.1

//Cache-Control: no-cache

//Host: foo.com:80

//Mime-Version: 1.0

//Content-Type: multipart-mixed ;

//boundary="251D738450A171593A1583EB"

//Content-Length: 1518

//Connection: close

}
