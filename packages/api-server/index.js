const express = require('express');
const jwt = require('jsonwebtoken');

const app = express();
const PORT = 3006;
const JWT_SECRET = 'your-secret-key'; // Change this in production

app.use(express.json());

// Middleware: Verify JWT Bearer token
const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
        return res.status(401).json({ message: 'Authentication token required' });
    }

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) {
            return res.status(403).json({ message: 'Invalid or expired token' });
        }
        req.user = user;
        next();
    });
};

// Middleware: Verify x-cdl-tenant-id header
const verifyTenantId = (req, res, next) => {
    const tenantId = req.headers['x-cdl-tenant-id'];

    if (tenantId !== 'test123') {
        return res.status(403).json({ message: 'Invalid tenant ID' });
    }

    next();
};

// Validate account_id format (5-10 digits)
const validateAccountId = (accountId) => {
    return accountId && /^\d{5,10}$/.test(accountId);
};

// Validate email format
const validateEmail = (email) => {
    return email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};

// [GET] /generate-token - Generate JWT token for testing
app.get('/generate-token', (req, res) => {
    console.log('[API] GET /generate-token - Generating JWT token');
    const token = jwt.sign({ userId: '123' }, JWT_SECRET, { expiresIn: '8h' });
    console.log('[API] Token generated successfully');
    res.status(200).json({
        message: 'Token generated successfully',
        token,
        expiresIn: '8h'
    });
});

// [GET] /get_email/:account_id
app.get('/get_email/:account_id', authenticateToken, verifyTenantId, (req, res) => {
    const { account_id } = req.params;
    console.log(`[API] GET /get_email/${account_id} - Request received`);

    if (!validateAccountId(account_id)) {
        console.log(`[API] Validation failed: Invalid account_id ${account_id}`);
        return res.status(400).json({
            message: 'Invalid account_id. Must be 5-10 digits'
        });
    }

    console.log(`[API] Email retrieved for account ${account_id}`);
    // Mock response - replace with actual database query
    res.status(200).json({
        message: 'Email retrieved successfully',
        account_id,
        email: 'user@example.com'
    });
});

// [POST] /change_email
app.post('/change_email', authenticateToken, verifyTenantId, (req, res) => {
    const { account_id, new_email } = req.body;
    console.log(`[API] POST /change_email - Request received for account ${account_id}`);

    if (!validateAccountId(account_id)) {
        console.log(`[API] Validation failed: Invalid account_id ${account_id}`);
        return res.status(400).json({
            message: 'Invalid account_id. Must be 5-10 digits'
        });
    }

    if (!validateEmail(new_email)) {
        console.log(`[API] Validation failed: Invalid email ${new_email}`);
        return res.status(400).json({
            message: 'Invalid email format'
        });
    }

    console.log(`[API] Email changed successfully: ${account_id} -> ${new_email}`);
    // Mock response - replace with actual database update
    res.status(200).json({
        message: 'Email changed successfully',
        account_id,
        new_email
    });
});

app.listen(PORT, () => {
    console.log(`API Server running on http://localhost:${PORT}`);
});
