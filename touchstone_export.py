"""
Project: Exporting touchstone files for an AEDT project
Author: Youngeun Na
Date: 2025-09-15
Version: 1.0
Description:
    - This is a script that exports touchstone files from a completed
      AEDT project that includes at least one optimetrics setup.
Dependencies:
    - PyAEDT 0.18.0
    - HFSS 2025 R1
"""

from pyaedt import Hfss
from pathlib import Path

# Folder to which the touchstone files are exported
touchstone_dir = r"D:\02_Users\UCIe" # Edit this
export_ts_to_dir = Path(touchstone_dir)
export_ts_to_dir.mkdir(parents = True, exist_ok = True)

# Open (or create) project/design in a fresh AEDT Desktop session
with Hfss(
    project = r"D:\02_Users\UCIe\01_channel_model\ucie_channel_2.0W_2.0S_2.0T_2.0H.aedt", # Edit this
    design = f"GSG_6Layer", # Edit this
    solution_type = "Terminal",
    version = "2025.1",
    new_desktop = True
) as hfss:

    # Optimetrics analysis and export of files
    def current_sweep(start, stop, step, unit = ""):
        values = []
        val = start
        while val <= stop + 1e-12:
            values.append(f"{val}{unit}")
            val += step
        return values

    sw_vals = current_sweep(1.5, 2.5, 0.5, "um") # Edit this
    mt_vals = current_sweep(2.0, 4.0, 1.0, "um") # Edit this
    dt_vals = current_sweep(2.0, 6.0, 2.0, "um") # Edit this

    sweep_values = {"SW": sw_vals, "MT": mt_vals, "DT": dt_vals}

    for sw_var in sw_vals:
        for mt_var in mt_vals:
            for dt_var in dt_vals:
                
                variations = ["SW", "MT", "DT"]
                variations_value = [sw_var, mt_var, dt_var]
                var_label = f"{sw_var}W_{mt_var}T_{dt_var}H"
    
                # Export touchstone file
                touchstone_name = f"GSG_{var_label}.s40p" # Edit port number if necessary
                touchstone_save_path = export_ts_to_dir / touchstone_name
    
                hfss.export_touchstone(
                    setup = "Setup1",
                    sweep = "Sweep",
                    output_file = touchstone_save_path,
                    variations = variations,
                    variations_value = variations_value,
                    renormalization = False,
                    impedance = 50,
                )
                print(f"✅ Exported touchstone: {touchstone_dir}")

    # Save project
    hfss.save_project()

print(f"Project finished ✨")



