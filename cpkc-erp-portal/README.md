# CPKC ERP Portal

A comprehensive Enterprise Resource Planning (ERP) portal built with Next.js, ShadCN UI, and Tailwind CSS for managing CPKC rail operations.

## 🚀 Features

### Core Modules
- **Dashboard** - Overview of operations with key metrics and recent activities
- **Waybills** - Complete waybill management and tracking
- **Contracts** - Customer contract management and pricing
- **Assets** - Rail asset inventory and status tracking
- **Operations** - Loading and offloading operation logging
- **Anomalies** - Anomaly detection, management, and resolution
- **Audit Trail** - Complete system activity tracking
- **Analytics** - Comprehensive reporting and insights
- **Chat Support** - AI-powered assistance for operations

### Key Capabilities
- Real-time data integration with Google Apps Script backend
- Responsive design optimized for desktop and mobile
- Advanced filtering and search across all modules
- Interactive charts and analytics
- Automated anomaly detection and resolution
- Complete audit trail for compliance
- Role-based access control
- Modern, intuitive user interface

## 🛠️ Technology Stack

- **Frontend**: Next.js 14, React 18, TypeScript
- **UI Components**: ShadCN UI, Radix UI primitives
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **Backend Integration**: Google Apps Script API
- **State Management**: React hooks and context

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cpkc-erp-portal
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   ```bash
   cp env.example .env.local
   ```
   
   Update the following variables in `.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec
   NEXT_PUBLIC_API_KEY=your_api_key_here
   NEXT_PUBLIC_AGENT_URL=http://localhost:8080
   ```

4. **Run the development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🏗️ Project Structure

```
cpkc-erp-portal/
├── src/
│   ├── app/                    # Next.js app router pages
│   │   ├── page.tsx           # Dashboard
│   │   ├── waybills/          # Waybill management
│   │   ├── contracts/         # Contract management
│   │   ├── assets/            # Asset management
│   │   ├── operations/        # Operations tracking
│   │   ├── anomalies/         # Anomaly management
│   │   ├── audit/             # Audit trail
│   │   ├── analytics/         # Analytics and reporting
│   │   ├── chat/              # Chat support
│   │   ├── settings/          # User settings
│   │   ├── layout.tsx         # Root layout
│   │   └── globals.css        # Global styles
│   ├── components/
│   │   ├── ui/                # ShadCN UI components
│   │   └── layout/            # Layout components
│   └── lib/
│       ├── api.ts             # API service layer
│       └── utils.ts           # Utility functions
├── public/                    # Static assets
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── README.md
```

## 🔧 Configuration

### API Integration

The portal integrates with a Google Apps Script backend that provides REST-like APIs for:

- **Waybills**: CRUD operations, status tracking
- **Contracts**: Contract management, pricing
- **Assets**: Asset inventory, status updates
- **Operations**: Operation logging, tracking
- **Anomalies**: Detection, resolution, management
- **Audit**: Activity logging, compliance tracking

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_API_URL` | Google Apps Script deployment URL | Yes |
| `NEXT_PUBLIC_API_KEY` | API authentication key | Yes |
| `NEXT_PUBLIC_APP_NAME` | Application name | No |
| `NEXT_PUBLIC_APP_VERSION` | Application version | No |

## 📱 Usage

### Dashboard
- View key performance indicators
- Monitor recent activities
- Quick access to important metrics

### Waybill Management
- Search and filter waybills
- Track shipment status
- View detailed waybill information
- Export data for reporting

### Contract Management
- Manage customer contracts
- Track pricing and terms
- Monitor contract validity
- Generate contract reports

### Asset Management
- Track rail assets (railcars, locomotives)
- Monitor asset status and utilization
- Schedule maintenance
- Generate asset reports

### Operations Tracking
- Log loading and offloading operations
- Track operation status
- Monitor crew activities
- Handle operation overrides

### Anomaly Management
- View detected anomalies
- Resolve issues automatically or manually
- Track resolution status
- Generate anomaly reports

### Analytics
- Interactive charts and graphs
- Performance metrics
- Trend analysis
- Custom reporting

### Chat Support
- AI-powered assistance
- Quick actions and suggestions
- Context-aware help
- System status monitoring

## 🎨 UI Components

The portal uses ShadCN UI components for a consistent, modern interface:

- **Cards**: Information display and organization
- **Tables**: Data presentation with sorting and filtering
- **Buttons**: Interactive elements with various styles
- **Badges**: Status indicators and labels
- **Tabs**: Content organization
- **Charts**: Data visualization with Recharts

## 🔒 Security

- API key authentication
- Role-based access control
- Secure data transmission
- Audit trail for all activities
- Input validation and sanitization

## 📊 Analytics

The analytics module provides:

- **Performance Metrics**: KPIs and key indicators
- **Trend Analysis**: Historical data visualization
- **Asset Utilization**: Resource usage tracking
- **Anomaly Trends**: Issue detection patterns
- **Operation Metrics**: Efficiency and throughput

## 🚀 Deployment

### Production Build

```bash
npm run build
npm start
```

### Environment Setup

1. Configure production environment variables
2. Set up Google Apps Script deployment
3. Configure API keys and permissions
4. Set up monitoring and logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is proprietary software for CPKC operations.

## 🆘 Support

For support and questions:
- Check the documentation
- Use the in-app chat support
- Contact the development team

## 🔄 Updates

The portal is regularly updated with:
- New features and improvements
- Bug fixes and security updates
- Performance optimizations
- UI/UX enhancements

---

**Built with ❤️ for CPKC Operations**
