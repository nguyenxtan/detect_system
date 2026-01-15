import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  Alert,
  TextField,
  InputAdornment,
  IconButton,
} from '@mui/material';
import {
  Search as SearchIcon,
  Image as ImageIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import Layout from '../components/layout/Layout';
import { defectAPI } from '../services/api';

function Incidents() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchIncidents();
  }, []);

  const fetchIncidents = async () => {
    try {
      setLoading(true);
      const response = await defectAPI.getIncidents();
      setIncidents(response.data);
      setError('');
    } catch (err) {
      console.error('Error fetching incidents:', err);
      // If endpoint doesn't exist yet, show friendly message
      if (err.response?.status === 404) {
        setError('Chức năng lịch sử đang được phát triển');
      } else {
        setError('Không thể tải lịch sử báo cáo');
      }
    } finally {
      setLoading(false);
    }
  };

  const filteredIncidents = incidents.filter((incident) =>
    incident.user_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    incident.predicted_defect_type?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <Layout>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Layout>
    );
  }

  return (
    <Layout>
      <Box>
        {/* Header */}
        <Box mb={4}>
          <Typography variant="h4" gutterBottom fontWeight="bold">
            Lịch Sử Báo Cáo Lỗi
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Theo dõi tất cả các báo cáo lỗi từ Telegram Bot
          </Typography>
        </Box>

        {error && (
          <Alert severity="info" sx={{ mb: 3 }}>
            {error}
            {error.includes('phát triển') && (
              <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                Hiện tại hệ thống đang ở Phase 1 - Chỉ có chức năng matching cơ bản.
                Incident logging sẽ được thêm vào Phase 2.
              </Typography>
            )}
          </Alert>
        )}

        {/* Search */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <TextField
              fullWidth
              placeholder="Tìm kiếm theo user ID hoặc loại lỗi..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon color="action" />
                  </InputAdornment>
                ),
              }}
            />
          </CardContent>
        </Card>

        {/* Incidents Table */}
        <Card>
          <CardContent>
            {filteredIncidents.length === 0 ? (
              <Box textAlign="center" py={8}>
                <ImageIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  Chưa có báo cáo nào
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Khi người dùng gửi ảnh vào Telegram bot, lịch sử sẽ hiển thị ở đây
                </Typography>
              </Box>
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell><strong>Thời gian</strong></TableCell>
                      <TableCell><strong>User ID</strong></TableCell>
                      <TableCell><strong>Loại lỗi</strong></TableCell>
                      <TableCell><strong>Độ tin cậy</strong></TableCell>
                      <TableCell><strong>Model version</strong></TableCell>
                      <TableCell align="center"><strong>Trạng thái</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredIncidents.map((incident) => (
                      <TableRow key={incident.id}>
                        <TableCell>
                          {new Date(incident.created_at).toLocaleString('vi-VN')}
                        </TableCell>
                        <TableCell>{incident.user_id}</TableCell>
                        <TableCell>
                          <Chip
                            label={incident.predicted_defect_type}
                            size="small"
                            color="primary"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={`${(incident.confidence * 100).toFixed(1)}%`}
                            size="small"
                            color={incident.confidence > 0.8 ? 'success' : incident.confidence > 0.6 ? 'warning' : 'error'}
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="caption" color="text.secondary">
                            {incident.model_version || 'v1.0'}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          {incident.confidence > 0.6 ? (
                            <CheckCircleIcon color="success" />
                          ) : (
                            <ErrorIcon color="error" />
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>

        {/* Stats Summary */}
        {filteredIncidents.length > 0 && (
          <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
            <Card sx={{ flex: 1 }}>
              <CardContent>
                <Typography variant="subtitle2" color="text.secondary">
                  Tổng báo cáo
                </Typography>
                <Typography variant="h4" fontWeight="bold">
                  {filteredIncidents.length}
                </Typography>
              </CardContent>
            </Card>
            <Card sx={{ flex: 1 }}>
              <CardContent>
                <Typography variant="subtitle2" color="text.secondary">
                  Độ tin cậy trung bình
                </Typography>
                <Typography variant="h4" fontWeight="bold" color="success.main">
                  {(
                    filteredIncidents.reduce((sum, i) => sum + i.confidence, 0) /
                    filteredIncidents.length * 100
                  ).toFixed(1)}%
                </Typography>
              </CardContent>
            </Card>
          </Box>
        )}
      </Box>
    </Layout>
  );
}

export default Incidents;
