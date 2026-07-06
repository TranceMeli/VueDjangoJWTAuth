from rest_framework_simplejwt.serializers import TokenObtainPairSerializer  # type: ignore[import]

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Rufe die Standard-Validierung auf (erzeugt den Token)
        data = super().validate(attrs)
        
        # Füge benutzerdefinierte Daten für das Frontend hinzu
        data['username'] = self.user.username
        data['isAdmin'] = self.user.is_staff # True, wenn Admin/Staff
        
        return data