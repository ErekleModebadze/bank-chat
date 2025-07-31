import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Chip,
  Avatar,
  IconButton,
  Tooltip,
  Collapse,
  Card,
  CardContent,
  Fade,
  useTheme
} from '@mui/material';
import {
  Person,
  SmartToy,
  Support,
  CreditCard,
  AccountBalance,
  ExpandMore,
  ExpandLess,
  ContentCopy,
  ThumbUp,
  ThumbDown,
  Schedule,
  CheckCircle
} from '@mui/icons-material';

const ChatBubble = ({
  message,
  isUser,
  agentName,
  timestamp,
  isTyping = false,
  showFeedback = false,
  onFeedback,
  onCopy
}) => {
  const theme = useTheme();
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const getAgentInfo = (agent) => {
    const agentMap = {
      'coordinator_agent': {
        icon: <Support />,
        name: 'Coordinator',
        color: theme.palette.primary.main,
        bgColor: theme.palette.primary.light
      },
      'card_operations_agent': {
        icon: <CreditCard />,
        name: 'Card Operations',
        color: theme.palette.success.main,
        bgColor: theme.palette.success.light
      },
      'loan_agent': {
        icon: <AccountBalance />,
        name: 'Loan Specialist',
        color: theme.palette.warning.main,
        bgColor: theme.palette.warning.light
      },
      'support_agent': {
        icon: <SmartToy />,
        name: 'Support',
        color: theme.palette.info.main,
        bgColor: theme.palette.info.light
      }
    };

    return agentMap[agent] || {
      icon: <SmartToy />,
      name: 'TBC Assistant',
      color: theme.palette.secondary.main,
      bgColor: theme.palette.secondary.light
    };
  };

  const agentInfo = !isUser ? getAgentInfo(agentName) : null;

  const handleCopy = async () => {
    if (onCopy) {
      await onCopy(message);
    } else {
      await navigator.clipboard.writeText(message);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatMessage = (text) => {
    // Enhanced message formatting
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
      .replace(/\*(.*?)\*/g, '<em>$1</em>') // Italic
      .replace(/`(.*?)`/g, '<code>$1</code>') // Code
      .replace(/₾(\d+(?:,\d{3})*(?:\.\d{2})?)/g, '<span style="font-weight: bold; color: #2e7d32;">₾$1</span>'); // Currency
  };

  if (isTyping) {
    return (
      <Fade in={true}>
        <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Avatar sx={{ bgcolor: agentInfo?.color, width: 32, height: 32 }}>
              {agentInfo?.icon}
            </Avatar>
            <Paper
              elevation={1}
              sx={{
                p: 2,
                backgroundColor: 'grey.100',
                borderRadius: 3,
                position: 'relative'
              }}
            >
              <Box sx={{ display: 'flex', gap: 0.5 }}>
                {[0, 1, 2].map((i) => (
                  <Box
                    key={i}
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      backgroundColor: 'grey.500',
                      animation: 'typing 1.4s infinite ease-in-out',
                      animationDelay: `${i * 0.2}s`,
                      '@keyframes typing': {
                        '0%, 80%, 100%': { opacity: 0.3 },
                        '40%': { opacity: 1 }
                      }
                    }}
                  />
                ))}
              </Box>
            </Paper>
          </Box>
        </Box>
      </Fade>
    );
  }

  return (
    <Fade in={true} timeout={300}>
      <Box
        sx={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          mb: 2,
          alignItems: 'flex-start',
        }}
      >
        {!isUser && (
          <Avatar
            sx={{
              bgcolor: agentInfo.color,
              mr: 1,
              mt: 1,
              width: 36,
              height: 36
            }}
          >
            {agentInfo.icon}
          </Avatar>
        )}

        <Box sx={{ maxWidth: '75%', minWidth: '200px' }}>
          {!isUser && (
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5, gap: 1 }}>
              <Chip
                label={agentInfo.name}
                size="small"
                sx={{
                  bgcolor: agentInfo.bgColor,
                  color: agentInfo.color,
                  fontWeight: 'medium'
                }}
              />
              {timestamp && (
                <Typography variant="caption" color="text.secondary">
                  {new Date(timestamp).toLocaleTimeString()}
                </Typography>
              )}
            </Box>
          )}

          <Card
            elevation={isUser ? 3 : 1}
            sx={{
              backgroundColor: isUser ? 'primary.main' : 'background.paper',
              color: isUser ? 'primary.contrastText' : 'text.primary',
              position: 'relative',
              '&:hover .message-actions': {
                opacity: 1
              }
            }}
          >
            <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
              <Typography
                variant="body1"
                sx={{
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  lineHeight: 1.5
                }}
                dangerouslySetInnerHTML={{
                  __html: formatMessage(message)
                }}
              />

              {/* Message Actions */}
              <Box
                className="message-actions"
                sx={{
                  position: 'absolute',
                  top: 4,
                  right: 4,
                  opacity: 0,
                  transition: 'opacity 0.2s',
                  display: 'flex',
                  gap: 0.5
                }}
              >
                <Tooltip title={copied ? "Copied!" : "Copy message"}>
                  <IconButton
                    size="small"
                    onClick={handleCopy}
                    sx={{
                      bgcolor: 'rgba(255,255,255,0.8)',
                      '&:hover': { bgcolor: 'rgba(255,255,255,0.9)' }
                    }}
                  >
                    {copied ? <CheckCircle fontSize="small" color="success" /> : <ContentCopy fontSize="small" />}
                  </IconButton>
                </Tooltip>

                {message.length > 200 && (
                  <Tooltip title={expanded ? "Show less" : "Show more"}>
                    <IconButton
                      size="small"
                      onClick={() => setExpanded(!expanded)}
                      sx={{
                        bgcolor: 'rgba(255,255,255,0.8)',
                        '&:hover': { bgcolor: 'rgba(255,255,255,0.9)' }
                      }}
                    >
                      {expanded ? <ExpandLess fontSize="small" /> : <ExpandMore fontSize="small" />}
                    </IconButton>
                  </Tooltip>
                )}
              </Box>

              {/* Feedback buttons for assistant messages */}
              {!isUser && showFeedback && (
                <Box sx={{ display: 'flex', gap: 1, mt: 1, justifyContent: 'flex-end' }}>
                  <Tooltip title="Helpful">
                    <IconButton
                      size="small"
                      onClick={() => onFeedback?.('positive')}
                      sx={{ color: 'success.main' }}
                    >
                      <ThumbUp fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Not helpful">
                    <IconButton
                      size="small"
                      onClick={() => onFeedback?.('negative')}
                      sx={{ color: 'error.main' }}
                    >
                      <ThumbDown fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              )}
            </CardContent>
          </Card>

          {isUser && timestamp && (
            <Typography
              variant="caption"
              sx={{
                display: 'block',
                textAlign: 'right',
                mt: 0.5,
                opacity: 0.7,
                fontSize: '0.75rem',
              }}
            >
              <Schedule fontSize="small" sx={{ mr: 0.5, verticalAlign: 'middle' }} />
              {new Date(timestamp).toLocaleTimeString()}
            </Typography>
          )}
        </Box>

        {isUser && (
          <Avatar sx={{ ml: 1, mt: 1, bgcolor: 'grey.500' }}>
            <Person />
          </Avatar>
        )}
      </Box>
    </Fade>
  );
};

export default ChatBubble;
