import React, { useState, useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Box,
  Chip,
  CircularProgress,
  Alert,
  ImageList,
  ImageListItem,
  Dialog,
  DialogContent,
  IconButton,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import BrokenImageIcon from '@mui/icons-material/BrokenImage';
import Layout from '../components/layout/Layout';
import { defectAPI } from '../services/api';

function DefectList() {
  const [defects, setDefects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedImage, setSelectedImage] = useState(null);
  const [openImageDialog, setOpenImageDialog] = useState(false);
  const [failedImages, setFailedImages] = useState(new Set());

  useEffect(() => {
    fetchDefects();
  }, []);

  const fetchDefects = async () => {
    try {
      setLoading(true);
      const response = await defectAPI.getProfiles();
      setDefects(response.data);
    } catch (err) {
      console.error('Error fetching defects:', err);
      setError('Không thể tải danh sách defects');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'major':
        return 'warning';
      case 'minor':
        return 'info';
      default:
        return 'default';
    }
  };

  const getSeverityLabel = (severity) => {
    switch (severity) {
      case 'critical':
        return 'Rất Nghiêm Trọng';
      case 'major':
        return 'Nghiêm Trọng';
      case 'minor':
        return 'Nhỏ';
      default:
        return severity;
    }
  };

  const handleImageClick = (imageUrl) => {
    setSelectedImage(imageUrl);
    setOpenImageDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenImageDialog(false);
    setSelectedImage(null);
  };

  const handleImageError = (imageUrl) => {
    console.error('Failed to load image:', imageUrl);
    setFailedImages(prev => new Set([...prev, imageUrl]));
  };

  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  return (
    <Layout>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Danh Sách Defect Profiles
        </Typography>
      </Box>

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {!loading && !error && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><strong>Khách Hàng</strong></TableCell>
                <TableCell><strong>Mã SP</strong></TableCell>
                <TableCell><strong>Tên SP</strong></TableCell>
                <TableCell><strong>Loại Lỗi</strong></TableCell>
                <TableCell><strong>Tiêu Đề</strong></TableCell>
                <TableCell><strong>Mức Độ</strong></TableCell>
                <TableCell><strong>Keywords</strong></TableCell>
                <TableCell><strong>Hình Ảnh Tham Khảo</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {defects.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <Typography variant="body2" color="textSecondary">
                      Chưa có defect profile nào
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                defects.map((defect) => (
                  <TableRow key={defect.id} hover>
                    <TableCell>{defect.customer}</TableCell>
                    <TableCell>{defect.part_code}</TableCell>
                    <TableCell>{defect.part_name}</TableCell>
                    <TableCell>
                      <Chip label={defect.defect_type} size="small" />
                    </TableCell>
                    <TableCell>{defect.defect_title}</TableCell>
                    <TableCell>
                      <Chip
                        label={getSeverityLabel(defect.severity)}
                        size="small"
                        color={getSeverityColor(defect.severity)}
                      />
                    </TableCell>
                    <TableCell>
                      {defect.keywords.join(', ')}
                    </TableCell>
                    <TableCell>
                      {defect.reference_images && defect.reference_images.length > 0 ? (
                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                          {defect.reference_images.map((imageUrl, index) => {
                            const fullImageUrl = `${API_BASE_URL}${imageUrl}`;
                            const hasFailed = failedImages.has(fullImageUrl);

                            return hasFailed ? (
                              <Box
                                key={index}
                                sx={{
                                  width: 60,
                                  height: 60,
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  borderRadius: 1,
                                  border: '1px solid #ddd',
                                  bgcolor: 'grey.100',
                                }}
                              >
                                <BrokenImageIcon sx={{ color: 'text.disabled', fontSize: 30 }} />
                              </Box>
                            ) : (
                              <Box
                                key={index}
                                component="img"
                                src={fullImageUrl}
                                alt={`${defect.defect_title} ${index + 1}`}
                                onClick={() => handleImageClick(fullImageUrl)}
                                onError={() => handleImageError(fullImageUrl)}
                                sx={{
                                  width: 60,
                                  height: 60,
                                  objectFit: 'cover',
                                  borderRadius: 1,
                                  cursor: 'pointer',
                                  border: '1px solid #ddd',
                                  '&:hover': {
                                    opacity: 0.8,
                                    transform: 'scale(1.05)',
                                    transition: 'all 0.2s',
                                  }
                                }}
                              />
                            );
                          })}
                        </Box>
                      ) : (
                        <Typography variant="body2" color="textSecondary">
                          Không có hình
                        </Typography>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Image Dialog for full-size view */}
      <Dialog
        open={openImageDialog}
        onClose={handleCloseDialog}
        maxWidth="lg"
        fullWidth
      >
        <DialogContent sx={{ position: 'relative', p: 0 }}>
          <IconButton
            onClick={handleCloseDialog}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
              bgcolor: 'rgba(0, 0, 0, 0.5)',
              color: 'white',
              '&:hover': {
                bgcolor: 'rgba(0, 0, 0, 0.7)',
              }
            }}
          >
            <CloseIcon />
          </IconButton>
          {selectedImage && (
            <Box
              component="img"
              src={selectedImage}
              alt="Full size"
              sx={{
                width: '100%',
                height: 'auto',
                display: 'block',
              }}
            />
          )}
        </DialogContent>
      </Dialog>
    </Layout>
  );
}

export default DefectList;
