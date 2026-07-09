import { Box, Button, Typography } from "@mui/material";
import AddIcon from "@mui/icons-material/Add";

const EmptyVault = ({ onAdd }) => (
  <Box
    sx={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      py: 10,
      gap: 2,
      bgcolor: "background.paper",
      borderRadius: 3,
      border: "1px dashed",
      borderColor: "divider",
    }}
  >
    <Box component="img" src="/dino.svg" alt="dino" sx={{ width: 96, height: 96, mb: 1 }} />
    <Typography variant="h6" sx={{ fontWeight: 600 }}>
      The vault is empty
    </Typography>
    <Typography
      variant="body2"
      sx={{ color: "text.secondary", textAlign: "center", maxWidth: 320 }}
    >
      Your prehistoric password guardian is standing by. Add your first password to get started.
    </Typography>
    <Button variant="contained" startIcon={<AddIcon />} onClick={onAdd} sx={{ mt: 1 }}>
      Add First Password
    </Button>
  </Box>
);

export default EmptyVault;
