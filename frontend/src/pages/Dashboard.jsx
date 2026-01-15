import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Grid,
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Box,
} from '@mui/material';
import {
  AddCircleOutline,
  ListAlt,
  TrendingUp,
} from '@mui/icons-material';
import Layout from '../components/layout/Layout';
import { isAdmin } from '../utils/auth';

function Dashboard() {
  const navigate = useNavigate();
  const userIsAdmin = isAdmin();

  const menuItems = [
    {
      title: 'Thêm Defect Profile',
      description: 'Tạo profile lỗi sản phẩm mới từ Excel + ảnh tham khảo',
      icon: <AddCircleOutline sx={{ fontSize: 60 }} />,
      path: '/defects/create',
      adminOnly: true,
    },
    {
      title: 'Danh Sách Defects',
      description: 'Xem và quản lý tất cả defect profiles',
      icon: <ListAlt sx={{ fontSize: 60 }} />,
      path: '/defects',
      adminOnly: false,
    },
    {
      title: 'Lịch Sử Báo Cáo',
      description: 'Xem lịch sử báo cáo từ Telegram Bot',
      icon: <TrendingUp sx={{ fontSize: 60 }} />,
      path: '/incidents',
      adminOnly: false,
    },
  ];

  return (
    <Layout>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Chào mừng đến với Hệ Thống Nhận Dạng Lỗi Sản Phẩm PU/PE
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {menuItems.map((item, index) => {
          if (item.adminOnly && !userIsAdmin) return null;

          return (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1, textAlign: 'center' }}>
                  <Box sx={{ color: 'primary.main', mb: 2 }}>
                    {item.icon}
                  </Box>
                  <Typography gutterBottom variant="h5" component="div">
                    {item.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {item.description}
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button
                    size="large"
                    fullWidth
                    variant="contained"
                    onClick={() => navigate(item.path)}
                  >
                    Mở
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      <Box sx={{ mt: 4, p: 3, bgcolor: 'background.paper', borderRadius: 2 }}>
        <Typography variant="h6" gutterBottom>
          Hướng Dẫn Sử Dụng
        </Typography>
        <Typography variant="body2" paragraph>
          <strong>1. Telegram Bot:</strong> Người dùng gửi ảnh lỗi sản phẩm → Bot trả về loại lỗi + mô tả QC chuẩn
        </Typography>
        <Typography variant="body2" paragraph>
          <strong>2. Admin Portal:</strong> Tạo và quản lý defect profiles (knowledge base)
        </Typography>
        <Typography variant="body2">
          <strong>3. AI Engine:</strong> Sử dụng CLIP model để matching image + text similarity
        </Typography>
      </Box>
    </Layout>
  );
}

export default Dashboard;
