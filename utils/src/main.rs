use std::env;
use std::fs::{self, File};
use std::io::{self, Read, Write};
use std::path::{Path, PathBuf};
use serde::Deserialize;
use thiserror::Error;
use reqwest::blocking::get;
use std::process;

#[derive(Debug, Deserialize)]
pub struct Config {
    pub title: String,
    pub url: String,
}

#[derive(Debug, Error)]
pub enum ConfigError {
    #[error("I/O error")]
    Io(#[from] io::Error),
    #[error("JSON deserialization error: {0}")]
    Json(#[from] serde_json::Error),
    #[error("HTTP request error: {0}")]
    Reqwest(#[from] reqwest::Error),
}

pub fn read_json_file(file_path: &str) -> Result<Vec<Config>, ConfigError> {
    let mut file = File::open(file_path)?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;

    // Print the contents of the file for debugging purposes
    println!("File content: {}", contents);

    let configs: Vec<Config> = serde_json::from_str(&contents)?;
    Ok(configs)
}

pub fn download_file(url: &str, dest: &Path) -> Result<(), ConfigError> {
    let response = get(url)?;
    let content = response.bytes()?;

    let mut file = File::create(dest)?;
    file.write_all(&content)?;
    Ok(())
}

fn main() {
    // Print the current working directory
    match env::current_dir() {
        Ok(path) => println!("Current directory: {}", path.display()),
        Err(e) => {
            eprintln!("Error getting current directory: {}", e);
            process::exit(1);
        },
    }

    let args: Vec<String> = env::args().collect();

    let file_path: String;

    if args.len() > 2 {
        eprintln!("Example Usage: cargo run <file_path>");
        process::exit(1);
    } else if args.len() == 1 {
        let mut input_path = String::new();
        
        println!("Enter the path to your JSON file: ");

        io::stdin().read_line(&mut input_path).unwrap();

        file_path = input_path.trim().to_string();
    } else {
        file_path = args[1].clone();
    }

    let configs = match read_json_file(&file_path) {
        Ok(configs) => configs,
        Err(e) => {
            eprintln!("Error reading JSON file '{}': {}", file_path, e);
            process::exit(1);
        },
    };

    let file_dir = Path::new(&file_path).parent().unwrap_or_else(|| Path::new("."));

    for config in configs {
        let file_name = format!("{}.txt", config.title.replace(" ", "_"));
        let dest_path = file_dir.join(file_name);

        match download_file(&config.url, &dest_path) {
            Ok(_) => println!("Downloaded '{}' to '{}'", config.title, dest_path.display()),
            Err(e) => eprintln!("Error downloading '{}': {}", config.title, e),
        }
    }
}
