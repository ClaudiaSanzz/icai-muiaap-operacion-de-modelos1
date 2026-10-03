"""TODO: contratos de entrada y salida de la inferencia."""

# Implementa WineQualityRequest y WineQualityPrediction con Pydantic.
# Revisa los campos de assets/inference_samples.csv y prohíbe columnas extra.

from pydantic import BaseModel, ConfigDict, Field

#class WineQualityRequest(BaseModel):
    #sample_id: int = Field(..., description="Unique identifier for the wine sample")
    #fixed_acidity: float = Field(..., description="Fixed acidity of the wine sample")
    #volatile_acidity: float = Field(..., description="volatile_acidity of the wine sample")
    #citric_acid: float = Field(..., description="citric_acid of the wine sample")
    #residual_sugar: float = Field(..., description="residual_sugar of the wine sample")
    #chlorides: float = Field(..., description="chlorides of the wine sample")
    #free_sulfur_dioxide: float = Field(..., description="free_sulfur_dioxide of the wine sample")
    #total_sulfur_dioxide: float = Field(..., description="total_sulfur_dioxide of the wine sample")
    #density: float = Field(..., description="density of the wine sample")
    #ph: float = Field(..., description="ph of the wine sample")
    #sulphates: float = Field(..., description="sulphates of the wine sample")
    #alcohol: float = Field(..., description="alcohol of the wine sample")

class WineQualityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fixed_acidity: float = Field(ge=0, le=20)
    volatile_acidity: float = Field(ge=0, le=2)
    citric_acid: float = Field(ge=0, le=2)
    residual_sugar: float = Field(ge=0, le=20)
    chlorides: float = Field(ge=0, le=1)
    free_sulfur_dioxide: float = Field(ge=0, le=100)
    total_sulfur_dioxide: float = Field(ge=0, le=300)
    density: float = Field(ge=0.98, le=1.01)
    ph: float = Field(ge=2.5, le=4.5)
    sulphates: float = Field(ge=0, le=3)
    alcohol: float = Field(ge=5, le=20)


class WineQualityPrediction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sample_id: str
    predicted_class: str
    confidence: float = Field(ge=0, le=1)
    model_version: str
    preprocessing_version: str