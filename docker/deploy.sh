#!/bin/bash

# ===========================================
# Social Media Automation Platform - Docker Deploy Script
# ===========================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    print_success "Docker and Docker Compose are installed"
}

# Check system requirements
check_system() {
    # Check available memory
    local mem_gb=$(free -g | awk 'NR==2{printf "%.0f", $2}')
    if [ "$mem_gb" -lt 4 ]; then
        print_warning "System has ${mem_gb}GB RAM. 4GB+ recommended for optimal performance."
    else
        print_success "System has ${mem_gb}GB RAM"
    fi

    # Check available disk space
    local disk_gb=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
    if [ "$disk_gb" -lt 10 ]; then
        print_warning "Only ${disk_gb}GB free disk space. 10GB+ recommended."
    else
        print_success "${disk_gb}GB free disk space available"
    fi
}

# Setup environment
setup_environment() {
    if [ ! -f ".env" ]; then
        print_status "Creating .env file from template..."
        cp .env.example .env
        print_warning "Please edit .env file with your actual credentials before running again!"
        print_status "Required: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET"
        exit 1
    else
        print_success "Environment file exists"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p gemini_automation/gemini_automation/auth/user_data
    mkdir -p downloaded_content
    mkdir -p logs
    mkdir -p ssl
    print_success "Directories created"
}

# Build and start services
deploy_services() {
    local mode=$1

    if [ "$mode" = "production" ]; then
        print_status "Starting production deployment..."
        docker-compose --profile production up -d --build
        print_success "Production deployment started"
        print_status "Access your application at: https://localhost"
        print_status "API documentation at: https://localhost/docs"
    else
        print_status "Starting development deployment..."
        docker-compose up -d --build
        print_success "Development deployment started"
        print_status "Access your application at: http://localhost:3000"
        print_status "API documentation at: http://localhost:8000/docs"
    fi
}

# Show status
show_status() {
    print_status "Deployment Status:"
    docker-compose ps
}

# Main menu
show_menu() {
    echo "========================================"
    echo "🐳 Social Media Automation - Docker Deploy"
    echo "========================================"
    echo "1. Deploy Development (Recommended)"
    echo "2. Deploy Production"
    echo "3. Show Status"
    echo "4. View Logs"
    echo "5. Stop Services"
    echo "6. Restart Services"
    echo "7. Cleanup"
    echo "8. Exit"
    echo "========================================"
}

# Main logic
main() {
    # Initial checks
    check_docker
    check_system

    while true; do
        show_menu
        read -p "Choose an option (1-8): " choice

        case $choice in
            1)
                print_status "Starting development deployment..."
                setup_environment
                create_directories
                deploy_services "development"
                sleep 5
                show_status
                ;;
            2)
                print_status "Starting production deployment..."
                if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
                    print_warning "SSL certificates not found in ssl/ directory"
                    read -p "Generate self-signed certificates? (y/n): " -n 1 -r
                    echo
                    if [[ $REPLY =~ ^[Yy]$ ]]; then
                        openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes -subj "/CN=localhost"
                        print_success "Self-signed certificates generated"
                    else
                        print_error "SSL certificates required for production. Exiting."
                        continue
                    fi
                fi
                setup_environment
                create_directories
                deploy_services "production"
                sleep 5
                show_status
                ;;
            3)
                show_status
                ;;
            4)
                echo "Select service to view logs:"
                echo "1. Backend"
                echo "2. Frontend"
                echo "3. All services"
                read -p "Choose (1-3): " log_choice
                case $log_choice in
                    1) docker-compose logs -f backend ;;
                    2) docker-compose logs -f frontend ;;
                    3) docker-compose logs -f ;;
                    *) print_error "Invalid choice" ;;
                esac
                ;;
            5)
                print_status "Stopping all services..."
                docker-compose down
                print_success "Services stopped"
                ;;
            6)
                print_status "Restarting services..."
                docker-compose restart
                print_success "Services restarted"
                ;;
            7)
                print_status "Cleaning up..."
                docker-compose down -v
                docker system prune -f
                print_success "Cleanup completed"
                ;;
            8)
                print_success "Goodbye! 👋"
                exit 0
                ;;
            *)
                print_error "Invalid option. Please choose 1-8."
                ;;
        esac

        echo
        read -p "Press Enter to continue..."
        clear
    done
}

# Run main function
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Social Media Automation Platform - Docker Deployment Script"
    echo ""
    echo "Usage: $0 [option]"
    echo ""
    echo "Options:"
    echo "  --help, -h    Show this help message"
    echo "  --dev         Quick development deployment"
    echo "  --prod        Quick production deployment"
    echo "  (no option)   Interactive menu mode"
    echo ""
    echo "Examples:"
    echo "  $0              # Interactive deployment"
    echo "  $0 --dev        # Quick development deploy"
    echo "  $0 --prod       # Quick production deploy"
    exit 0
elif [ "$1" = "--dev" ]; then
    check_docker
    check_system
    setup_environment
    create_directories
    deploy_services "development"
elif [ "$1" = "--prod" ]; then
    check_docker
    check_system
    setup_environment
    create_directories
    deploy_services "production"
else
    main
fi