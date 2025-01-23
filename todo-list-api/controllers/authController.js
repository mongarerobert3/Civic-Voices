const User = require('../models/User'); // Ensure you import your User model
const jwt = require('jsonwebtoken');

// Register a new user
exports.register = async (req, res) => {
    const { name, email, password } = req.body;

    try {
        const user = new User({ name, email, password });
        await user.save();

        const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: '1h' });
        res.status(201).json({ token, message: 'Registration successful.' });
    } catch (error) {
        console.error('Error during registration:', error);
        res.status(500).json({ error: 'Something went wrong during registration.' });
    }
};

// Login an existing user
exports.login = async (req, res) => {
	const { email, password } = req.body;

	try {
			// Find the user by email
			const user = await User.findOne({ email });
			if (!user) {
					return handleLoginError(res, 'Invalid email or password.');
			}

			// Compare the provided password with the stored hashed password
			const isMatch = await user.comparePassword(password);
			if (!isMatch) {
					return handleLoginError(res, 'Invalid email or password.');
			}

			// Generate JWT token
			const token = generateToken(user._id);
			
			console.log('User logged in successfully:', user.email);
			return res.status(200).json({ token, message: 'Login successful.' });
	} catch (error) {
			console.error('Error during login:', error);
			return res.status(500).json({ error: 'Something went wrong. Please try again.' });
	}
};

// Helper function to handle login errors
const handleLoginError = (res, message) => {
	console.log(message);
	return res.status(401).json({ error: message });
};

// Helper function to generate JWT token
const generateToken = (userId) => {
	return jwt.sign({ id: userId }, process.env.JWT_SECRET, { expiresIn: '1h' });
};
