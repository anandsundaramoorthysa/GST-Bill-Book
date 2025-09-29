## GST Bill Book

### Table of Contents
- About Project
- Installation
- Use / Run the Project
- Features
- Screenshots (optional)
- Contribution
- License
- Contact Me

### About Project
GST Bill Book is a Flask-based mini-application to manage GST invoicing, products, inventory, and basic customer insights. It includes user authentication, invoice creation with PDF export, and a clean Bootstrap UI with a shared layout.

### Installation
1) Clone the repository
```bash
git clone https://github.com/anandsundaramoorthysa/GST-Bill-Book.git
cd GST-Bill-Book
```
2) Create a virtual environment and install requirements (Windows PowerShell)
```bash
py -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -r requirements.txt
```
3) (Optional) Set environment variables for Flask
```bash
$env:FLASK_ENV="development"
```

### Use / Run the Project
```bash
.\.venv\Scripts\python app.py
```
Then open `http://127.0.0.1:5000` in your browser.

### Features
- User signup and login (session-based)
- Create invoices with items, quantities, discount, tax
- Generate invoice PDF using ReportLab
- View invoice list and detailed invoice page
- Manage products and inventory (CRUD)
- Customer monthly spending summary
- Profile page with business details

### Screenshots (optional)
You can add screenshots of the Home, Invoices, and New Invoice pages here.

### Contribution
Contributions are welcome! Please:
- Fork the repo and create a feature branch
- Make your changes with clear commit messages
- Open a pull request describing the changes

### License

This project is released under the MIT License. You are free to use, modify, and distribute the code under the terms of this license. See the [LICENSE](LICENSE) file in the repository for the full text.

### Contact Me
If you have any questions or would like to collaborate, feel free to reach out:
- Email: [sanand03072005@gmail.com](mailto:sanand03072005@gmail.com?subject=Inquiry%20About%20GST%20Bill%20Book&body=Hi%20Anand,%0A%0AI'm%20interested%20in%20learning%20more%20about%20the%20GST%20Bill%20Book%20you%20developed.%20I%20have%20some%20questions%20about%20its%20features,%20invoice%20generation,%20and%20possible%20collaboration.%0A%0AThank%20you!%0A%0ABest%20regards,%0A[Your%20Name])
- LinkedIn: [Anand Sundaramoorthy](https://www.linkedin.com/in/anandsundaramoorthysa/)



