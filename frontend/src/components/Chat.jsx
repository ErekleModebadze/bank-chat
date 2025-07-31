import React, {useState, useRef, useEffect} from 'react';
import {
    Box,
    TextField,
    IconButton,
    Paper,
    Typography,
    CircularProgress,
    Alert,
    Container,
    AppBar,
    Toolbar,
} from '@mui/material';
import {Send, AccountBalanceWallet} from '@mui/icons-material';
import ChatMessage from './ChatMessage';
import {chatAPI} from '../services/api';

const Chat = () => {
    const [messages, setMessages] = useState([
        {
            id: 1,
            message: "გამარჯობა! მე ვარ TBC ბანკის ვირტუალური ასისტენტი. როგორ შემიძლია დაგეხმაროთ?\n\nHello! I'm TBC Bank's virtual assistant. How can I help you today?",
            isUser: false,
            agentName: 'coordinator_agent',
            timestamp: new Date().toISOString(),
        }
    ]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState(null);
    const [error, setError] = useState(null);
    const messagesEndRef = useRef(null);

    // Mock customer ID (in production, get from authentication)
    const customerId = 'CUST001';

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({behavior: 'smooth'});
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async () => {
        if (!inputMessage.trim() || isLoading) return;

        const userMessage = {
            id: Date.now(),
            message: inputMessage,
            isUser: true,
            timestamp: new Date().toISOString(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInputMessage('');
        setIsLoading(true);
        setError(null);

        try {
            const response = await chatAPI.sendMessage(inputMessage, customerId, sessionId);

            // Update session ID if this is the first message
            if (!sessionId) {
                setSessionId(response.session_id);
            }

            const assistantMessage = {
                id: Date.now() + 1,
                message: response.response,
                isUser: false,
                agentName: response.agent_name,
                timestamp: new Date().toISOString(),
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (err) {
            console.error('Error sending message:', err);
            setError('Failed to send message. Please try again.');

            const errorMessage = {
                id: Date.now() + 1,
                message: "I apologize, but I'm experiencing technical difficulties. Please try again in a moment.",
                isUser: false,
                agentName: 'support_agent',
                timestamp: new Date().toISOString(),
            };

            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    };

    const quickActions = [
        {text: 'Block my card', emoji: '🔒'},
        {text: 'Check loan limits', emoji: '💰'},
        {text: 'Recent transactions', emoji: '📊'},
        {text: 'Contact information', emoji: '📞'},
    ];

    return (
        <Box sx={{height: '100vh', width: "100vw", display: 'flex', flexDirection: 'column'}}>
            <AppBar position="static">
                <Toolbar>
                    <AccountBalanceWallet sx={{mr: 2}}/>
                    <Typography variant="h6" component="div" sx={{flexGrow: 1}}>
                        TBC Bank Assistant
                    </Typography>
                    <Typography variant="body2">
                        Customer: {customerId}
                    </Typography>
                </Toolbar>
            </AppBar>

            <Container maxWidth="md" sx={{flex: 1, display: 'flex', flexDirection: 'column', py: 2}}>
                {error && (
                    <Alert severity="error" sx={{mb: 2}} onClose={() => setError(null)}>
                        {error}
                    </Alert>
                )}

                <Paper
                    elevation={2}
                    sx={{
                        flex: 1,
                        display: 'flex',
                        flexDirection: 'column',
                        overflow: 'hidden',
                    }}
                >
                    <Box
                        sx={{
                            flex: 1,
                            overflowY: 'auto',
                            p: 2,
                            backgroundColor: '#fafafa',
                        }}
                    >
                        {messages.map((msg) => (
                            <ChatMessage
                                key={msg.id}
                                message={msg.message}
                                isUser={msg.isUser}
                                agentName={msg.agentName}
                                timestamp={msg.timestamp}
                            />
                        ))}

                        {isLoading && (
                            <Box sx={{display: 'flex', justifyContent: 'flex-start', mb: 2}}>
                                <Box sx={{display: 'flex', alignItems: 'center', p: 2}}>
                                    <CircularProgress size={20} sx={{mr: 1}}/>
                                    <Typography variant="body2" color="text.secondary">
                                        TBC Assistant is typing...
                                    </Typography>
                                </Box>
                            </Box>
                        )}

                        <div ref={messagesEndRef}/>
                    </Box>

                    {/* Quick Actions */}
                    <Box sx={{p: 2, borderTop: 1, borderColor: 'divider', backgroundColor: 'white'}}>
                        <Typography variant="body2" color="text.secondary" sx={{mb: 1}}>
                            Quick actions:
                        </Typography>
                        <Box sx={{display: 'flex', flexWrap: 'wrap', gap: 1}}>
                            {quickActions.map((action, index) => (
                                <Paper
                                    key={index}
                                    elevation={0}
                                    sx={{
                                        px: 2,
                                        py: 1,
                                        backgroundColor: 'grey.100',
                                        cursor: 'pointer',
                                        '&:hover': {
                                            backgroundColor: 'grey.200',
                                        },
                                    }}
                                    onClick={() => {
                                        setInputMessage(action.text);
                                    }}
                                >
                                    <Typography variant="body2">
                                        {action.emoji} {action.text}
                                    </Typography>
                                </Paper>
                            ))}
                        </Box>
                    </Box>

                    {/* Input Area */}
                    <Box
                        sx={{
                            p: 2,
                            borderTop: 1,
                            borderColor: 'divider',
                            backgroundColor: 'white',
                        }}
                    >
                        <Box sx={{display: 'flex', gap: 1}}>
                            <TextField
                                fullWidth
                                multiline
                                maxRows={4}
                                placeholder="Type your message here... (Georgian or English)"
                                value={inputMessage}
                                onChange={(e) => setInputMessage(e.target.value)}
                                onKeyPress={handleKeyPress}
                                disabled={isLoading}
                                variant="outlined"
                                size="small"
                            />
                            <IconButton
                                color="primary"
                                onClick={sendMessage}
                                disabled={!inputMessage.trim() || isLoading}
                                sx={{alignSelf: 'flex-end'}}
                            >
                                <Send/>
                            </IconButton>
                        </Box>
                    </Box>
                </Paper>
            </Container>
        </Box>
    );
};

export default Chat;
