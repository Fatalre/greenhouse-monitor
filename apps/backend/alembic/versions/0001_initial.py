"""Initial greenhouse schema."""
import sqlalchemy as sa

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "admin_users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_admin_users_username", "admin_users", ["username"])
    op.create_table(
        "devices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("device_id", sa.String(120), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("api_key_hash", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("device_id"),
    )
    op.create_index("ix_devices_device_id", "devices", ["device_id"])
    op.create_table(
        "experiments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_id", sa.String(120), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("external_id"),
    )
    op.create_index("ix_experiments_external_id", "experiments", ["external_id"])
    op.create_table(
        "measurements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("device_id", sa.Integer(), sa.ForeignKey("devices.id"), nullable=False),
        sa.Column("experiment_id", sa.Integer(), sa.ForeignKey("experiments.id")),
        sa.Column("sample", sa.Integer(), nullable=False),
        sa.Column("measured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("timestamp_source", sa.String(10), nullable=False),
        sa.Column("uptime_ms", sa.Integer()),
        sa.Column("lux", sa.Float()),
        sa.Column("dht22_temperature_c", sa.Float()),
        sa.Column("dht22_humidity_percent", sa.Float()),
        sa.Column("bme680_temperature_c", sa.Float()),
        sa.Column("bme680_humidity_percent", sa.Float()),
        sa.Column("bme680_pressure_hpa", sa.Float()),
        sa.Column("bme680_gas_resistance_kohm", sa.Float()),
        sa.Column("soil_raw", sa.Integer()),
        sa.Column("soil_moisture_percent", sa.Float()),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint(
            "device_id", "sample", "experiment_id",
            name="uq_measurement_idempotency",
            postgresql_nulls_not_distinct=True,
        ),
    )
    op.create_index("ix_measurements_measured_at", "measurements", ["measured_at"])
    op.create_index("ix_measurements_device_id", "measurements", ["device_id"])
    op.create_index("ix_measurements_experiment_id", "measurements", ["experiment_id"])
    op.create_index("ix_measurements_device_measured", "measurements", ["device_id", "measured_at"])
    op.create_index("ix_measurements_experiment_measured", "measurements", ["experiment_id", "measured_at"])
    op.create_table(
        "thermocouple_measurements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "measurement_id", sa.Integer(),
            sa.ForeignKey("measurements.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("sensor_number", sa.Integer(), nullable=False),
        sa.Column("temperature_c", sa.Float()),
    )
    op.create_index(
        "ix_thermocouple_measurements_measurement_id",
        "thermocouple_measurements", ["measurement_id"],
    )
    op.create_index(
        "ix_thermocouple_measurements_sensor_number",
        "thermocouple_measurements", ["sensor_number"],
    )
    op.create_index(
        "ix_tc_measurement_sensor",
        "thermocouple_measurements", ["measurement_id", "sensor_number"],
    )

def downgrade():
    op.drop_table("thermocouple_measurements")
    op.drop_table("measurements")
    op.drop_table("experiments")
    op.drop_table("devices")
    op.drop_table("admin_users")
