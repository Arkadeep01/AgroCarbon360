## backend/src/farmer/forms.py
from fastapi import Form

class FarmerForm:
    """
    Helper class to parse Farmer form submissions (HTML form data).
    Usage:
    farmer_form = await FarmerForm.as_form(...)
    """

    def __init__(
        self,
        name: str = Form(...),
        email: str = Form(...),
        phone_number: str = Form(...),
        address: str | None = Form(None),
        farm_name: str | None = Form(None),
        farm_location: str | None = Form(None),
        farm_size: int | None = Form(None),
        crop_type: str | None = Form(None),
        irrigation_type: str | None = Form(None),
        soil_type: str | None = Form(None),
        notes: str | None = Form(None),
        status: str | None = Form("active"),
        profile_picture: str | None = Form(None),
        identification_number: str | None = Form(None),
    ):
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.address = address
        self.farm_name = farm_name
        self.farm_location = farm_location
        self.farm_size = farm_size
        self.crop_type = crop_type
        self.irrigation_type = irrigation_type
        self.soil_type = soil_type
        self.notes = notes
        self.status = status
        self.profile_picture = profile_picture
        self.identification_number = identification_number

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        email: str = Form(...),
        phone_number: str = Form(...),
        address: str | None = Form(None),
        farm_name: str | None = Form(None),
        farm_location: str | None = Form(None),
        farm_size: int | None = Form(None),
        crop_type: str | None = Form(None),
        irrigation_type: str | None = Form(None),
        soil_type: str | None = Form(None),
        notes: str | None = Form(None),
        status: str | None = Form("active"),
        profile_picture: str | None = Form(None),
        identification_number: str | None = Form(None),
    ):
        return cls(
            name=name,
            email=email,
            phone_number=phone_number,
            address=address,
            farm_name=farm_name,
            farm_location=farm_location,
            farm_size=farm_size,
            crop_type=crop_type,
            irrigation_type=irrigation_type,
            soil_type=soil_type,
            notes=notes,
            status=status,
            profile_picture=profile_picture,
            identification_number=identification_number,
        )