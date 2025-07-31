import React from 'react';
import { Box, Typography, Paper, Chip } from '@mui/material';
import { Person, SmartToy, Support, CreditCard, AccountBalance } from '@mui/icons-material';

const ChatMessage = ({ message, isUser, agentName, timestamp }) => {
  const getAgentIcon = (agent) => {
    switch (agent) {
      case 'coordinator_agent':
        return <Support />;
      case 'card_operations_agent':
        return <CreditCard />;
      case 'loan_agent':
        return <AccountBalance />;
      case 'support_agent':
        return <SmartToy />;
      default:
        return <SmartToy />;
    }
  };

  const getAgentName = (agent) => {
    switch (agent) {
      case 'coordinator_agent':
        return 'Coordinator';
      case 'card_operations_agent':
        return 'Card Operations';
      case 'loan_agent':
        return 'Loan Specialist';
      case 'support_agent':
        return 'Support';
      default:
        return 'TBC Assistant';
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 2,
        alignItems: 'flex-start',
      }}
    >
      {!isUser && (
        <Box sx={{ mr: 1, mt: 1 }}>
          {getAgentIcon(agentName)}
        </Box>
      )}

      <Box sx={{ maxWidth: '70%' }}>
        {!isUser && (
          <Chip
            label={getAgentName(agentName)}
            size="small"
            sx={{ mb: 1 }}
            color="primary"
            variant="outlined"
          />
        )}

        <Paper
          elevation={1}
          sx={{
            p: 2,
            backgroundColor: isUser ? 'primary.main' : 'grey.100',
            color: isUser ? 'primary.contrastText' : 'text.primary',
          }}
        >
          <Typography
            variant="body1"
            sx={{
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
            }}
          >
            {message}
          </Typography>

          {timestamp && (
            <Typography
              variant="caption"
              sx={{
                display: 'block',
                mt: 1,
                opacity: 0.7,
                fontSize: '0.75rem',
              }}
            >
              {new Date(timestamp).toLocaleTimeString()}
            </Typography>
          )}
        </Paper>
      </Box>

      {isUser && (
        <Box sx={{ ml: 1, mt: 1 }}>
          <Person />
        </Box>
      )}
    </Box>
  );
};

export default ChatMessage;
