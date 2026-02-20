# Mission Requirements Document (MRD) - EagleEye-1 Project
**Revision:** 1.0 | **Status:** Engineering Draft

## 1. Mission Statement
The primary objective of the EagleEye-1 system is Earth observation in the Mid-Wave Infrared (MWIR) spectrum for the early detection and monitoring of forest fires, demonstrating onboard image processing capabilities.

## 2. System-Level Requirements

### 2.1. Physical Architecture and Constraints
* **[REQ-SYS-010]** The system SHALL comply with the 3U CubeSat Design Specification (Cal Poly CDS Rev. 14).
* **[REQ-SYS-020]** The total launch mass of the system SHALL NOT exceed 4.00 kg (including margins).
* **[REQ-SYS-030]** The Center of Gravity (CG) SHALL be located within a 2.0 cm radius of the system's geometric center.

### 2.2. Orbital Requirements
* **[REQ-ORB-010]** The system SHALL operate in a Sun-Synchronous Low Earth Orbit (SSO LEO).
* **[REQ-ORB-020]** The nominal orbit altitude SHALL be 500 km (± 20 km).
* **[REQ-ORB-030]** The Local Time of Descending Node (LTDN) SHALL be set to 10:30 AM to optimize thermal illumination conditions.

### 2.3. Payload
* **[REQ-PAY-010]** The payload SHALL consist of a Mid-Wave Infrared (MWIR) optical sensor.
* **[REQ-PAY-020]** The system SHALL provide a Ground Sampling Distance (GSD) of less than 50 meters per pixel from the nominal altitude.

### 2.4. Attitude Determination and Control System (ADCS)
* **[REQ-ADC-010]** The system SHALL be capable of pointing the payload towards Nadir during observation mode.
* **[REQ-ADC-020]** The steady-state pointing error SHALL NOT exceed 0.1 degrees in all 3 axes.

### 2.5. Electrical Power System (EPS)
* **[REQ-EPS-010]** The system SHALL generate sufficient electrical power to support the operational payload for a minimum of 15 minutes per orbit.
* **[REQ-EPS-020]** The system SHALL maintain a positive energy balance at the end of each full orbit (End-of-Orbit Battery Depth of Discharge < 20%).