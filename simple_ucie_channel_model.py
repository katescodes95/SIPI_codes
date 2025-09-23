"""
Project: Channel Modeling in Various Configurations for UCIe
Author: Youngeun Na
Date: 2025-09-01
Version: 1.0
Description:
    - This is a script that models a channel interface in two different configurations
      (split and staggered) for UCIe applications.
    - Touchstone files are exported for post-processing.
Dependencies:
    - PyAEDT 0.18.0
    - HFSS 2025 R1
"""

from pyaedt import Hfss
from pathlib import Path

# Parameters
sw = 2.0
ss = 2.0
mt = 2.0
dh = 2.0

sw_str = str(sw)
ss_str = str(ss)
mt_str = str(mt)
dh_str = str(dh)

# Folder to which the results are exported
csv_dir = r"D:\02_Users\UCIe\csv" # Edit this
export_csv_to_dir = Path(csv_dir)
export_csv_to_dir.mkdir(parents = True, exist_ok = True)

# Folder to which the touchstone files are exported
touchstone_dir = r"D:\02_Users\UCIe\touchstone" # Edit this
export_ts_to_dir = Path(touchstone_dir)
export_ts_to_dir.mkdir(parents = True, exist_ok = True)

# Open (or create) project/design in a fresh AEDT Desktop session
with Hfss(
    project = f"ucie_channel_{sw_str}W_{ss_str}S_{mt_str}T_{dh_str}H",
    design = f"SSS_{sw_str}W_{ss_str}S_{mt_str}T_{dh_str}H",
    solution_type = "Terminal",
    version = "2025.1",
    new_desktop = True
) as hfss:

    # Save project to path
    project_dir = Path(r"D:\02_Users\UCIe") # Edit this
    project_name = f"ucie_channel_{sw_str}W_{ss_str}S_{mt_str}T_{dh_str}H.aedt"
    project_save_path = project_dir / project_name

    project_dir.mkdir(parents = True, exist_ok = True)

    hfss.save_project(str(project_save_path))
    print(f"✅ Project saved to {project_save_path}.")

    # Project settings
    hfss.modeler.model_units = "um"
    hfss.change_material_override(material_override = True)
    hfss.change_automatically_use_causal_materials(lossy_dielectric = True)

    # Project variables
    hfss["$bound_margin"] = "5um"
    hfss["$sub_margin"] = "5um"
    hfss["$sw"] = sw_str + "um"
    hfss["$ss"] = ss_str + "um"
    hfss["$mt"] = mt_str + "um"
    hfss["$dh"] = dh_str + "um"
    hfss["$model_length"] = "10um"
    hfss["$bound_marginZ"] = "5um"
    hfss["$sub_marginZ"] = "5um"
    hfss["$total_length"] = "2mm"

    # Origins
    boundary_origin = [0, 0, 0]
    sub_origin = ["$bound_margin", 0, "$bound_marginZ"]
    gnd_origin = ["$bound_margin + $sub_margin", 0, "$bound_marginZ + $sub_marginZ"]
    sig_origin = ["$bound_margin + $sub_margin", 0, "$bound_marginZ + $sub_marginZ + $mt + $dh"]
    port_origin = ["$bound_margin + $sub_margin - 0.25*$sw", 0, "$bound_marginZ + $sub_marginZ + $mt + $dh - 0.25*$mt"]

    # Add dielectric material
    hfss.materials.add_material("HD8930")
    hfss.materials["HD8930"].permittivity = 3.1
    hfss.materials["HD8930"].dielectric_loss_tangent = 0.01

    # Build the boundary region
    boundary_region = hfss.modeler.create_box(
        origin = boundary_origin,
        sizes = ["2*$bound_margin + 2*$sub_margin + 10*$sw + 9*$ss",
                "$model_length",
                "2*$bound_marginZ + 2*$sub_marginZ + 4*$mt + 3*$dh"],
        name = "boundary",
        material = "vacuum",
        transparency = 0.9,
        color = (128, 255, 255)
    )

    # Build the substrate
    substrate_region = hfss.modeler.create_box(
        origin = sub_origin,
        sizes = ["2*$sub_margin + 10*$sw + 9*$ss",
                "$model_length",
                "2*$sub_marginZ + 4*$mt + 3*$dh"],
        name = "dielectric",
        material = "HD8930",
        transparency = 0.9,
        color = (0, 128, 128)
    )

    # Build the ground traces
    gnd_trace = hfss.modeler.create_box(
        origin = gnd_origin,
        sizes = ["$sw",
                "$model_length",
                "$mt"],
        name = "G41",
        material = "copper",
        transparency=0.0,
        color = (145, 175, 143)
    )

    hfss.modeler.duplicate_along_line(
        "G41",
        vector = ["$sw + $ss", 0, 0],
        clones = 10,
        attach = False
    )

    old_gnd_names = [f"G41_{i}" if i > 0 else "G41" for i in range (10)]
    new_gnd_names = [f"G4{hex(i)[2:].upper()}" for i in range(1,11)]

    for old, new in zip(old_gnd_names, new_gnd_names):
        obj = hfss.modeler[old]
        if obj:
            obj.name = new
            print(f"✅ Renamed {old} to {new}")
        else:
            print(f"⚠ Ground trace {old} not found.")

    gnd_objs = [hfss.modeler[o] for o in hfss.modeler.object_names if o.startswith("G")]

    for i in gnd_objs:
        hfss.modeler.duplicate_along_line(
            i,
            vector = [0, 0, "2*$mt + 2*$dh"],
            clones = 2,
            attach = False
        )

    old_gnd_names = [f"G4{hex(i)[2:].upper()}_1" for i in range(1,11)]
    new_gnd_names = [f"G2{hex(i)[2:].upper()}" for i in range(1,11)]

    for old, new in zip(old_gnd_names, new_gnd_names):
        obj = hfss.modeler[old]
        if obj:
            obj.name = new
            print(f"✅ Renamed {old} to {new}")
        else:
            print(f"⚠ Ground trace {old} not found.")

    # Build the signal traces
    sig_trace = hfss.modeler.create_box(
        origin = sig_origin,
        sizes = ["$sw",
                "$model_length",
                "$mt"],
        name = "S31",
        material = "copper",
        transparency = 0.0,
        color = (175, 175, 143),
        solve_inside = True
    )

    hfss.modeler.duplicate_along_line(
        "S31",
        vector = ["$sw + $ss", 0, 0],
        clones = 10,
        attach = False
    )

    old_sig_names = [f"S31_{i}" if i > 0 else "S31" for i in range (10)]
    new_sig_names = [f"S3{hex(i)[2:].upper()}" for i in range(1,11)]

    for old, new in zip(old_sig_names, new_sig_names):
        obj = hfss.modeler[old]
        if obj:
            obj.name = new
            print(f"✅ Renamed {old} to {new}")
        else:
            print(f"⚠ Signal trace {old} not found.")

    sig_objs = [hfss.modeler[o] for o in hfss.modeler.object_names if o.startswith("S")]

    for i in sig_objs:
        hfss.modeler.duplicate_along_line(
            i,
            vector = [0, 0, "2*$mt + 2*$dh"],
            clones = 2,
            attach = False
        )

    old_sig_names = [f"S3{hex(i)[2:].upper()}_1" for i in range(1,11)]
    new_sig_names = [f"S1{hex(i)[2:].upper()}" for i in range(1,11)]

    for old, new in zip(old_sig_names, new_sig_names):
        obj = hfss.modeler[old]
        if obj:
            obj.name = new
            print(f"✅ Renamed {old} to {new}")
        else:
            print(f"⚠ Signal trace {old} not found.")

    # Create ports
    port = hfss.modeler.create_rectangle(
        orientation = "Y",
        origin = port_origin,
        sizes = ["$mt + 0.5*$mt", "$sw + 0.5*$sw"],
        name = "port31"
    )

    hfss.modeler.duplicate_along_line(
        "port31",
        vector = ["$sw + $ss", 0, 0],
        clones = 10,
        attach = False
    )

    old_port_names = [f"port31_{i}" if i > 0 else "port31" for i in range (10)]
    new_port_names = [f"port3{hex(i)[2:].upper()}" for i in range(1,11)]

    for old, new in zip(old_port_names, new_port_names):
        obj = hfss.modeler[old]
        if obj:
            obj.name = new
            print(f"✅ Renamed {old} to {new}")
        else:
            print(f"⚠ {old} not found.")

    port_objs = [hfss.modeler[o] for o in hfss.modeler.object_names if o.startswith("port")]

    for i in port_objs:
        hfss.modeler.duplicate_along_line(
            i,
            vector = [0, 0, "2*$mt + 2*$dh"],
            clones = 2,
            attach = False
        )

    old_port_names = [f"port3{hex(i)[2:].upper()}_1" for i in range(1,11)]
    new_port_names = [f"port1{hex(i)[2:].upper()}" for i in range(1,11)]

    for old, new in zip(old_port_names, new_port_names):
        obj = hfss.modeler[old]
        if obj:
            obj.name = new
            print(f"✅ Renamed {old} to {new}")
        else:
            print(f"⚠ {old} not found.")

    all_port_objs = [hfss.modeler[o] for o in hfss.modeler.object_names if o.startswith("port")]

    for i in all_port_objs:
        hfss.modeler.duplicate_along_line(
            i,
            vector = [0, "$model_length", 0],
            clones = 2,
            attach = False
        )

    # Create perfect E boundaries
    PerfE1 = hfss.modeler.create_rectangle(
        orientation = "Y",
        origin = sub_origin,
        sizes = ["2*$sub_marginZ + 4*$mt + 3*$dh", "2*$sub_margin + 10*$sw + 9*$ss"],
        name = "PE_T1"
    )

    PerfE2 = hfss.modeler.create_rectangle(
        orientation = "Y",
        origin = ["$bound_margin", "$model_length", "$bound_marginZ"],
        sizes = ["2*$sub_marginZ + 4*$mt + 3*$dh", "2*$sub_margin + 10*$sw + 9*$ss"],
        name = "PE_T2"
    )

    all_port_objs = hfss.modeler.object_names

    term1_ports = [name for name in all_port_objs if name.startswith("port") and not name.endswith("_1")]
    term2_ports  = [name for name in all_port_objs if name.startswith("port") and name.endswith("_1")]

    hfss.modeler.subtract(
        blank_list = "PE_T1",
        tool_list = term1_ports,
        keep_originals = True
    )

    hfss.modeler.subtract(
        blank_list = "PE_T2",
        tool_list = term2_ports,
        keep_originals = True
    )

    # Assign perfect E
    yneg_face = min(PerfE1.faces, key = lambda f: f.center[1])
    ypos_face = max(PerfE2.faces, key = lambda f: f.center[1])

    selected_faces_for_perfE = [yneg_face.id, ypos_face.id]
    hfss.assign_perfect_e(selected_faces_for_perfE, name = "PerfE")

    # Create lumped ports
    all_sig_objs = [name for name in hfss.modeler.object_names if name.startswith("S")]

    hfss.modeler.subtract(
        blank_list = term1_ports,
        tool_list = all_sig_objs,
        keep_originals = True
    )

    hfss.modeler.subtract(
        blank_list = term2_ports,
        tool_list = all_sig_objs,
        keep_originals = True
    )

    # Assign lumped ports
    term1_ports = []

    for i in range(1,11):
        if i < 10:
            term1_ports.append(f"port3{i}")
        else:
            term1_ports.append("port3A")

    for i in range(1,11):
        if i < 10:
            term1_ports.append(f"port1{i}")
        else:
            term1_ports.append("port1A")

    term2_ports = [p + "_1" for p in term1_ports]

    for pname in term1_ports:
        hfss.lumped_port(
            assignment = pname,
            reference = "PE_T1",
            deembed = "-($total_length - $model_length)/2",
            terminals_rename = False
        )

    for pname in term2_ports:
        hfss.lumped_port(
            assignment = pname,
            reference = "PE_T2",
            deembed = "-($total_length - $model_length)/2",
            terminals_rename = False
        )

    # Assign radiation boundary
    faces_for_rad = boundary_region.faces

    top_face = max(faces_for_rad, key = lambda f: f.center[2])
    bottom_face = min(faces_for_rad, key = lambda f: f.center[2])
    xpos_face = max(faces_for_rad, key = lambda f: f.center[0])
    xneg_face = min(faces_for_rad, key = lambda f: f.center[0])

    selected_faces_for_rad = [top_face.id, bottom_face.id, xpos_face.id, xneg_face.id]
    hfss.assign_radiation_boundary_to_faces(selected_faces_for_rad, name = "Rad1")

    # Add solution setup
    setup = hfss.create_setup(
        name = "Setup1",
        setup_type = "HFSSDriven",
        SolveType = "Single",
        Frequency = "50GHz",
        MaxDeltaS = 0.02,
        MaximumPasses = 20,
        MinimumPasses = 2,
        MinimumConvergedPasses = 2,
        PercentRefinement = 25,
        SaveAnyFields = True,
        SaveRadFieldsOnly = False
    )

    # Add frequency sweep
    linear_step_sweep = setup.create_linear_step_sweep(
        name = "Sweep",
        unit = "GHz",
        start_frequency = 0,
        stop_frequency = 40,
        step_size = 0.025,
        save_fields = False,
        save_rad_fields = False,
        sweep_type = "Interpolating"
    )

    # Optimetrics
    param_setup = hfss.parametrics.add(
        variable = "$sw",
        start_point = "2um",
        end_point = "3um",
        step = "0.5um",
        variation_type = "LinearStep"
    )

    param_setup.add_variation(
        sweep_variable = "$mt",
        start_point = "2um",
        end_point = "3um",
        step = "0.5um",
        variation_type = "LinearStep"
    )

    # Validate design
    hfss.validate_full_design()

    # Analyze
    param_setup.analyze(cores = 32, tasks = 1)

    # Create report and export files
    expressions_for_RL = ["dB(St(S11_T1,S11_T1))", "dB(St(S12_T1,S12_T1))", "dB(St(S13_T1,S13_T1))", "dB(St(S14_T1,S14_T1))", "dB(St(S15_T1,S15_T1))",
                        "dB(St(S16_T1,S16_T1))", "dB(St(S17_T1,S17_T1))", "dB(St(S18_T1,S18_T1))", "dB(St(S19_T1,S19_T1))", "dB(St(S1A_T1,S1A_T1))",
                        "dB(St(S31_T1,S31_T1))", "dB(St(S32_T1,S32_T1))", "dB(St(S33_T1,S33_T1))", "dB(St(S34_T1,S34_T1))", "dB(St(S35_T1,S35_T1))",
                        "dB(St(S36_T1,S36_T1))", "dB(St(S37_T1,S37_T1))", "dB(St(S38_T1,S38_T1))", "dB(St(S39_T1,S39_T1))", "dB(St(S3A_T1,S3A_T1))"]
    expressions_for_IL = ["dB(St(S11_T2,S11_T1))", "dB(St(S12_T2,S12_T1))", "dB(St(S13_T2,S13_T1))", "dB(St(S14_T2,S14_T1))", "dB(St(S15_T2,S15_T1))",
                        "dB(St(S16_T2,S16_T1))", "dB(St(S17_T2,S17_T1))", "dB(St(S18_T2,S18_T1))", "dB(St(S19_T2,S19_T1))", "dB(St(S1A_T2,S1A_T1))",
                        "dB(St(S31_T2,S31_T1))", "dB(St(S32_T2,S32_T1))", "dB(St(S33_T2,S33_T1))", "dB(St(S34_T2,S34_T1))", "dB(St(S35_T2,S35_T1))",
                        "dB(St(S36_T2,S36_T1))", "dB(St(S37_T2,S37_T1))", "dB(St(S38_T2,S38_T1))", "dB(St(S39_T2,S39_T1))", "dB(St(S3A_T2,S3A_T1))"]

    report1 = hfss.post.reports_by_category.terminal_solution(
        expressions = expressions_for_RL,
        setup = "Setup1 : Sweep"
    )
    report1.create("Return Loss")

    report2 = hfss.post.reports_by_category.terminal_solution(
        expressions = expressions_for_IL,
        setup = "Setup1 : Sweep"
    )
    report2.create("Insertion Loss")

    # Export graphs as csv
    hfss.post.export_report_to_file(
        output_dir = csv_dir,
        plot_name = "Return Loss",
        extension = ".csv"
    )
    print(f"✅ Exported to CSV: {csv_dir}")

    hfss.post.export_report_to_file(
        output_dir = csv_dir,
        plot_name = "Insertion Loss",
        extension = ".csv"
    )
    print(f"✅ Exported to CSV: {csv_dir}")

    # Export touchstone file
    touchstone_name = f"SSS_{sw_str}W_{ss_str}S_{mt_str}T_{dh_str}H.s40p" # Edit this
    touchstone_save_path = export_ts_to_dir / touchstone_name

    hfss.export_touchstone(
        output_file = touchstone_save_path,
        renormalization = False,
        impedance = 50,
    )
    print(f"✅ Exported touchstone: {touchstone_dir}")

    # Save project
    hfss.save_project()

    # Optimetrics analysis and export of files
    def current_sweep(start, stop, step, unit = ""):
        values = []
        val = start
        while val <= stop + 1e-12:
            values.append(f"{val}{unit}")
            val += step
        return values

    sw_vals = current_sweep(2, 3, 0.5, "um") # Edit this
    mt_vals = current_sweep(2, 3, 0.5, "um") # Edit this

    sweep_values = {"$sw": sw_vals, "$mt": mt_vals}

    for sw_var in sw_vals:
        for mt_var in mt_vals:

            # Definitions
            variations = {
                "$sw": sw_var,
                "$mt": mt_var,
            }
            variations_value = [sw_var, mt_var]
            var_label = f"{sw_var}W_{mt_var}T_2.0H"

            # Export touchstone file
            touchstone_name = f"SSS_{var_label}.s40p" # Edit this
            touchstone_save_path = export_ts_to_dir / touchstone_name

            hfss.export_touchstone(
                output_file = touchstone_save_path,
                variations = ["$sw", "$mt"],
                variations_value = variations_value,
                renormalization = False,
                impedance = 50,
            )
            print(f"✅ Exported touchstone: {touchstone_dir}")

            # Create IL report
            hfss.post.create_report(
                expressions = expressions_for_IL,
                variations = variations,
                plot_name = f"IL_{var_label}"
            )

            # Export IL graphs as csv
            hfss.post.export_report_to_file(
                output_dir = csv_dir,
                plot_name = f"IL_{var_label}",
                extension = ".csv"
            )
            print(f"✅ Exported to CSV: {csv_dir}")

            # Create RL report
            hfss.post.create_report(
                expressions = expressions_for_RL,
                variations = variations,
                plot_name = f"RL_{var_label}"
            )

            # Export RL graphs as csv
            hfss.post.export_report_to_file(
                output_dir = csv_dir,
                plot_name = f"RL_{var_label}",
                extension = ".csv"
            )
            print(f"✅ Exported to CSV: {csv_dir}")

    # Save project
    hfss.save_project()





    # Create new design
    hfss.insert_design(name = f"GSG_{sw_str}W_{ss_str}S_{mt_str}T_{dh_str}H", solution_type = "Terminal") # Edit this
    hfss.set_active_design(f"GSG_{sw_str}W_{ss_str}S_{mt_str}T_{dh_str}H") # Edit this

    # Build the boundary region
    boundary_region = hfss.modeler.create_box(
        origin=boundary_origin,
        sizes=["2*$bound_margin + 2*$sub_margin + 10*$sw + 9*$ss",
               "$model_length",
               "2*$bound_marginZ + 2*$sub_marginZ + 4*$mt + 3*$dh"],
        name="boundary",
        material="vacuum",
        transparency=0.9,
        color=(128, 255, 255)
    )

    # Build the substrate
    substrate_region = hfss.modeler.create_box(
        origin=sub_origin,
        sizes=["2*$sub_margin + 10*$sw + 9*$ss",
               "$model_length",
               "2*$sub_marginZ + 4*$mt + 3*$dh"],
        name="dielectric",
        material="HD8930",
        transparency=0.9,
        color=(0, 128, 128)
    )

    # Build L4 and L2
    gnd_trace = hfss.modeler.create_box(
        origin=gnd_origin,
        sizes=["$sw",
               "$model_length",
               "$mt"],
        name="G41",
        material="copper",
        transparency=0.0,
        color=(145, 175, 143)
    )

    hfss.modeler.duplicate_along_line(
        "G41",
        vector=["2*$sw + 2*$ss", 0, 0],
        clones=5,
        attach=False
    )

    old_gnd_names = [f"G41_{i}" if i > 0 else "G41" for i in range(5)]
    new_gnd_names = [f"G4{2*i+1}" for i in range(5)]

    for old, new in zip(old_gnd_names, new_gnd_names):
        obj = hfss.modeler[old]
        if obj:
            obj.name = new
            print(f"✅ Renamed {old} to {new}")
        else:
            print(f"⚠ Ground trace {old} not found.")

    gnd_objs = [hfss.modeler[o] for o in hfss.modeler.object_names if o.startswith("G4")]

    for i in gnd_objs:
        hfss.modeler.duplicate_along_line(
            i,
            vector=[0, 0, "2*$mt + 2*$dh"],
            clones=2,
            attach=False
        )

    old_gnd_names = [f"G4{2*i+1}_1" for i in range(5)]
    new_gnd_names = [f"G2{2*i+1}" for i in range(5)]

    for old, new in zip(old_gnd_names, new_gnd_names):
        obj = hfss.modeler[old]
        if obj:
            obj.name = new
            print(f"✅ Renamed {old} to {new}")
        else:
            print(f"⚠ Ground trace {old} not found.")

    new_sig_origin = ["$bound_margin + $sub_margin + $sw + $ss", 0, "$bound_marginZ + $sub_marginZ"]
    sig_trace = hfss.modeler.create_box(
        origin=new_sig_origin,
        sizes=["$sw",
               "$model_length",
               "$mt"],
        name="S42",
        material="copper",
        transparency=0.0,
        color=(175, 175, 143),
        solve_inside=True
    )

    hfss.modeler.duplicate_along_line(
        "S42",
        vector=["2*$sw + 2*$ss", 0, 0],
        clones=5,
        attach=False
    )

    old_sig_names = ["S42"] + [f"S42_{i}" for i in range(1,5)]
    new_sig_names = [f"S4{hex(2*i)[2:].upper()}" for i in range(1,6)]

    for old, new in zip(old_sig_names, new_sig_names):
        obj = hfss.modeler[old]
        if obj:
            obj.name = new
            print(f"✅ Renamed {old} to {new}")
        else:
            print(f"⚠ Signal trace {old} not found.")

    sig_objs = [hfss.modeler[o] for o in hfss.modeler.object_names if o.startswith("S4")]

    for i in sig_objs:
        hfss.modeler.duplicate_along_line(
            i,
            vector=[0, 0, "2*$mt + 2*$dh"],
            clones=2,
            attach=False
        )

    old_sig_names = [f"S4{2*i}_1" for i in range(1,5)] + ["S4A_1"]
    new_sig_names = [f"S2{hex(2*i)[2:].upper()}" for i in range(1, 6)]

    for old, new in zip(old_sig_names, new_sig_names):
        obj = hfss.modeler[old]
        if obj:
            obj.name = new
            print(f"✅ Renamed {old} to {new}")
        else:
            print(f"⚠ Signal trace {old} not found.")

    # Build L3 and L1
    new_gnd_origin = ["$bound_margin + $sub_margin + $sw + $ss", 0, "$bound_marginZ + $sub_marginZ + $mt + $dh"]
    gnd_trace = hfss.modeler.create_box(
        origin = new_gnd_origin,
        sizes = ["$sw",
                "$model_length",
                "$mt"],
        name = "G32",
        material = "copper",
        transparency=0.0,
        color = (145, 175, 143)
    )

    hfss.modeler.duplicate_along_line(
        "G32",
        vector = ["2*$sw + 2*$ss", 0, 0],
        clones = 5,
        attach = False
    )

    old_gnd_names = ["G32"] + [f"G32_{i}" for i in range(1,5)]
    new_gnd_names = [f"G3{hex(2*i)[2:].upper()}" for i in range(1,6)]

    for old, new in zip(old_gnd_names, new_gnd_names):
        obj = hfss.modeler[old]
        if obj:
            obj.name = new
            print(f"✅ Renamed {old} to {new}")
        else:
            print(f"⚠ Ground trace {old} not found.")

    gnd_objs = [hfss.modeler[o] for o in hfss.modeler.object_names if o.startswith("G3")]

    for i in gnd_objs:
        hfss.modeler.duplicate_along_line(
            i,
            vector = [0, 0, "2*$mt + 2*$dh"],
            clones = 2,
            attach = False
        )

    old_gnd_names = [f"G3{2*i}_1" for i in range(1,5)] + ["G3A_1"]
    new_gnd_names = [f"G1{hex(2*i)[2:].upper()}" for i in range(1,6)]

    for old, new in zip(old_gnd_names, new_gnd_names):
        obj = hfss.modeler[old]
        if obj:
            obj.name = new
            print(f"✅ Renamed {old} to {new}")
        else:
            print(f"⚠ Ground trace {old} not found.")

    new_sig_origin = ["$bound_margin + $sub_margin", 0, "$bound_marginZ + $sub_marginZ + $mt + $dh"]
    sig_trace = hfss.modeler.create_box(
        origin = new_sig_origin,
        sizes = ["$sw",
                "$model_length",
                "$mt"],
        name = "S31",
        material = "copper",
        transparency = 0.0,
        color = (175, 175, 143),
        solve_inside = True
    )

    hfss.modeler.duplicate_along_line(
        "S31",
        vector = ["2*$sw + 2*$ss", 0, 0],
        clones = 5,
        attach = False
    )

    old_sig_names = [f"S31_{i}" if i > 0 else "S31" for i in range(5)]
    new_sig_names = [f"S3{2*i+1}" for i in range(5)]

    for old, new in zip(old_sig_names, new_sig_names):
        obj = hfss.modeler[old]
        if obj:
            obj.name = new
            print(f"✅ Renamed {old} to {new}")
        else:
            print(f"⚠ Signal trace {old} not found.")

    sig_objs = [hfss.modeler[o] for o in hfss.modeler.object_names if o.startswith("S3")]

    for i in sig_objs:
        hfss.modeler.duplicate_along_line(
            i,
            vector = [0, 0, "2*$mt + 2*$dh"],
            clones = 2,
            attach = False
        )

    old_sig_names = [f"S3{2*i+1}_1" for i in range(5)]
    new_sig_names = [f"S1{2*i+1}" for i in range(5)]

    for old, new in zip(old_sig_names, new_sig_names):
        obj = hfss.modeler[old]
        if obj:
            obj.name = new
            print(f"✅ Renamed {old} to {new}")
        else:
            print(f"⚠ Signal trace {old} not found.")

    # Create ports in L4 and L2
    new_port_origin = ["$bound_margin + $sub_margin + $sw + $ss - 0.25*$sw", 0, "$bound_marginZ + $sub_marginZ - 0.25*$mt"]
    port = hfss.modeler.create_rectangle(
        orientation = "Y",
        origin = new_port_origin,
        sizes = ["$mt + 0.5*$mt", "$sw + 0.5*$sw"],
        name = "port42"
    )

    hfss.modeler.duplicate_along_line(
        "port42",
        vector = ["2*$sw + 2*$ss", 0, 0],
        clones = 5,
        attach = False
    )

    old_port_names = ["port42"] + [f"port42_{i}" for i in range(1,5)]
    new_port_names = [f"port4{hex(2*i)[2:].upper()}" for i in range(1,6)]

    for old, new in zip(old_port_names, new_port_names):
        obj = hfss.modeler[old]
        if obj:
            obj.name = new
            print(f"✅ Renamed {old} to {new}")
        else:
            print(f"⚠ {old} not found.")

    port_objs = [hfss.modeler[o] for o in hfss.modeler.object_names if o.startswith("port4")]

    for i in port_objs:
        hfss.modeler.duplicate_along_line(
            i,
            vector = [0, 0, "2*$mt + 2*$dh"],
            clones = 2,
            attach = False
        )

    old_port_names = [f"port4{2*i}_1" for i in range(1,5)] + ["port4A_1"]
    new_port_names = [f"port2{hex(2*i)[2:].upper()}" for i in range(1,6)]

    for old, new in zip(old_port_names, new_port_names):
        obj = hfss.modeler[old]
        if obj:
            obj.name = new
            print(f"✅ Renamed {old} to {new}")
        else:
            print(f"⚠ {old} not found.")

    # Create ports in L3 and L1
    new_port_origin = ["$bound_margin + $sub_margin - 0.25*$sw", 0, "$bound_marginZ + $sub_marginZ + $mt + $dh - 0.25*$mt"]
    port = hfss.modeler.create_rectangle(
        orientation = "Y",
        origin = new_port_origin,
        sizes = ["$mt + 0.5*$mt", "$sw + 0.5*$sw"],
        name = "port31"
    )

    hfss.modeler.duplicate_along_line(
        "port31",
        vector = ["2*$sw + 2*$ss", 0, 0],
        clones = 5,
        attach = False
    )

    old_port_names = [f"port31_{i}" if i > 0 else "port31" for i in range(5)]
    new_port_names = [f"port3{2*i+1}" for i in range(5)]

    for old, new in zip(old_port_names, new_port_names):
        obj = hfss.modeler[old]
        if obj:
            obj.name = new
            print(f"✅ Renamed {old} to {new}")
        else:
            print(f"⚠ {old} not found.")

    port_objs = [hfss.modeler[o] for o in hfss.modeler.object_names if o.startswith("port3")]

    for i in port_objs:
        hfss.modeler.duplicate_along_line(
            i,
            vector = [0, 0, "2*$mt + 2*$dh"],
            clones = 2,
            attach = False
        )

    old_port_names = [f"port3{2*i+1}_1" for i in range(5)]
    new_port_names = [f"port1{2*i+1}" for i in range(5)]

    for old, new in zip(old_port_names, new_port_names):
        obj = hfss.modeler[old]
        if obj:
            obj.name = new
            print(f"✅ Renamed {old} to {new}")
        else:
            print(f"⚠ {old} not found.")

    all_port_objs = [hfss.modeler[o] for o in hfss.modeler.object_names if o.startswith("port")]

    for i in all_port_objs:
        hfss.modeler.duplicate_along_line(
            i,
            vector = [0, "$model_length", 0],
            clones = 2,
            attach = False
        )

    # Create perfect E boundaries
    PerfE1 = hfss.modeler.create_rectangle(
        orientation = "Y",
        origin = sub_origin,
        sizes = ["2*$sub_marginZ + 4*$mt + 3*$dh", "2*$sub_margin + 10*$sw + 9*$ss"],
        name = "PE_T1"
    )

    PerfE2 = hfss.modeler.create_rectangle(
        orientation = "Y",
        origin = ["$bound_margin", "$model_length", "$bound_marginZ"],
        sizes = ["2*$sub_marginZ + 4*$mt + 3*$dh", "2*$sub_margin + 10*$sw + 9*$ss"],
        name = "PE_T2"
    )

    all_port_objs = hfss.modeler.object_names

    term1_ports = [name for name in all_port_objs if name.startswith("port") and not name.endswith("_1")]
    term2_ports  = [name for name in all_port_objs if name.startswith("port") and name.endswith("_1")]

    hfss.modeler.subtract(
        blank_list = "PE_T1",
        tool_list = term1_ports,
        keep_originals = True
    )

    hfss.modeler.subtract(
        blank_list = "PE_T2",
        tool_list = term2_ports,
        keep_originals = True
    )

    # Assign perfect E
    yneg_face = min(PerfE1.faces, key = lambda f: f.center[1])
    ypos_face = max(PerfE2.faces, key = lambda f: f.center[1])

    selected_faces_for_perfE = [yneg_face.id, ypos_face.id]
    hfss.assign_perfect_e(selected_faces_for_perfE, name = "PerfE")

    # Create lumped ports
    all_sig_objs = [name for name in hfss.modeler.object_names if name.startswith("S")]

    hfss.modeler.subtract(
        blank_list = term1_ports,
        tool_list = all_sig_objs,
        keep_originals = True
    )

    hfss.modeler.subtract(
        blank_list = term2_ports,
        tool_list = all_sig_objs,
        keep_originals = True
    )

    # Assign lumped ports
    term1_ports = []

    for i in range(2,11,2):
        if i < 10:
            term1_ports.append(f"port4{i}")
        else:
            term1_ports.append("port4A")

    for i in range(2,11,2):
        if i < 10:
            term1_ports.append(f"port2{i}")
        else:
            term1_ports.append("port2A")

    for i in range(1,10,2):
        term1_ports.append(f"port3{i}")

    for i in range(1,10,2):
        term1_ports.append(f"port1{i}")

    term2_ports = [p + "_1" for p in term1_ports]

    for pname in term1_ports:
        hfss.lumped_port(
            assignment = pname,
            reference = "PE_T1",
            deembed = "-($total_length - $model_length)/2",
            terminals_rename = False
        )

    for pname in term2_ports:
        hfss.lumped_port(
            assignment = pname,
            reference = "PE_T2",
            deembed = "-($total_length - $model_length)/2",
            terminals_rename = False
        )

    # Assign radiation boundary
    faces_for_rad = boundary_region.faces

    top_face = max(faces_for_rad, key = lambda f: f.center[2])
    bottom_face = min(faces_for_rad, key = lambda f: f.center[2])
    xpos_face = max(faces_for_rad, key = lambda f: f.center[0])
    xneg_face = min(faces_for_rad, key = lambda f: f.center[0])

    selected_faces_for_rad = [top_face.id, bottom_face.id, xpos_face.id, xneg_face.id]
    hfss.assign_radiation_boundary_to_faces(selected_faces_for_rad, name = "Rad1")

    # Add solution setup
    setup = hfss.create_setup(
        name = "Setup1",
        setup_type = "HFSSDriven",
        SolveType = "Single",
        Frequency = "50GHz",
        MaxDeltaS = 0.02,
        MaximumPasses = 20,
        MinimumPasses = 2,
        MinimumConvergedPasses = 2,
        PercentRefinement = 25,
        SaveAnyFields = True,
        SaveRadFieldsOnly = False
    )

    # Add frequency sweep
    linear_step_sweep = setup.create_linear_step_sweep(
        name = "Sweep",
        unit = "GHz",
        start_frequency = 0,
        stop_frequency = 40,
        step_size = 0.025,
        save_fields = False,
        save_rad_fields = False,
        sweep_type = "Interpolating"
    )

    # Optimetrics
    param_setup = hfss.parametrics.add(
        variable = "$sw",
        start_point = "2um",
        end_point = "3um",
        step = "0.5um",
        variation_type = "LinearStep"
    )

    param_setup.add_variation(
        sweep_variable = "$mt",
        start_point = "2um",
        end_point = "3um",
        step = "0.5um",
        variation_type = "LinearStep"
    )

    # Validate design
    hfss.validate_full_design()

    # Analyze
    param_setup.analyze(cores = 32, tasks = 1)

    # Create report
    expressions_for_RL = ["dB(St(S11_T1,S11_T1))", "dB(St(S13_T1,S13_T1))", "dB(St(S15_T1,S15_T1))", "dB(St(S17_T1,S17_T1))", "dB(St(S19_T1,S19_T1))",
                        "dB(St(S22_T1,S22_T1))", "dB(St(S24_T1,S24_T1))", "dB(St(S26_T1,S26_T1))", "dB(St(S28_T1,S28_T1))", "dB(St(S2A_T1,S2A_T1))",
                        "dB(St(S31_T1,S31_T1))", "dB(St(S33_T1,S33_T1))", "dB(St(S35_T1,S35_T1))", "dB(St(S37_T1,S37_T1))", "dB(St(S39_T1,S39_T1))",
                        "dB(St(S12_T1,S12_T1))", "dB(St(S14_T1,S14_T1))", "dB(St(S16_T1,S16_T1))", "dB(St(S18_T1,S18_T1))", "dB(St(S1A_T1,S1A_T1))"]
    expressions_for_IL = ["dB(St(S11_T2,S11_T1))", "dB(St(S12_T2,S12_T1))", "dB(St(S13_T2,S13_T1))", "dB(St(S14_T2,S14_T1))", "dB(St(S15_T2,S15_T1))",
                        "dB(St(S22_T2,S22_T1))", "dB(St(S24_T2,S24_T1))", "dB(St(S26_T2,S26_T1))", "dB(St(S28_T2,S28_T1))", "dB(St(S2A_T2,S2A_T1))",
                        "dB(St(S31_T2,S31_T1))", "dB(St(S32_T2,S32_T1))", "dB(St(S33_T2,S33_T1))", "dB(St(S34_T2,S34_T1))", "dB(St(S35_T2,S35_T1))",
                        "dB(St(S12_T2,S12_T1))", "dB(St(S14_T2,S14_T1))", "dB(St(S16_T2,S16_T1))", "dB(St(S18_T2,S18_T1))", "dB(St(S1A_T2,S1A_T1))"]

    report1 = hfss.post.reports_by_category.terminal_solution(
        expressions = expressions_for_RL,
        setup = "Setup1 : Sweep"
    )
    report1.create("Return Loss")

    report2 = hfss.post.reports_by_category.terminal_solution(
        expressions = expressions_for_IL,
        setup = "Setup1 : Sweep"
    )
    report2.create("Insertion Loss")

    # Export graphs as csv
    hfss.post.export_report_to_file(
        output_dir = csv_dir,
        plot_name = "Return Loss",
        extension = ".csv"
    )
    print(f"✅ Exported to CSV: {csv_dir}")

    hfss.post.export_report_to_file(
        output_dir = csv_dir,
        plot_name = "Insertion Loss",
        extension = ".csv"
    )
    print(f"✅ Exported to CSV: {csv_dir}")

    # Export touchstone file
    touchstone_name = f"GSG_{sw_str}W_{ss_str}S_{mt_str}T_{dh_str}H.s40p" # Edit this
    touchstone_save_path = export_ts_to_dir / touchstone_name

    hfss.export_touchstone(
        output_file = touchstone_save_path,
        renormalization = False,
        impedance = 50,
    )
    print(f"✅ Exported touchstone: {touchstone_dir}")

    # Save project
    hfss.save_project()

    # Optimetrics analysis and export of files
    sw_vals = current_sweep(2, 3, 0.5, "um") # Edit this
    mt_vals = current_sweep(2, 3, 0.5, "um") # Edit this

    sweep_values = {"$sw": sw_vals, "$mt": mt_vals}

    for sw_var in sw_vals:
        for mt_var in mt_vals:

            # Definitions
            variations = {
                "$sw": sw_var,
                "$mt": mt_var,
            }
            variations_value = [sw_var, mt_var]
            var_label = f"{sw_var}W_{mt_var}T_2.0H"

            # Export touchstone file
            touchstone_name = f"GSG_{var_label}.s40p" # Edit this
            touchstone_save_path = export_ts_to_dir / touchstone_name

            hfss.export_touchstone(
                output_file = touchstone_save_path,
                variations = ["$sw", "$mt"],
                variations_value = variations_value,
                renormalization = False,
                impedance = 50,
            )
            print(f"✅ Exported touchstone: {touchstone_dir}")

            # Create IL report
            hfss.post.create_report(
                expressions = expressions_for_IL,
                variations = variations,
                plot_name = f"IL_{var_label}"
            )

            # Export IL graphs as csv
            hfss.post.export_report_to_file(
                output_dir = csv_dir,
                plot_name = f"IL_{var_label}",
                extension = ".csv"
            )
            print(f"✅ Exported to CSV: {csv_dir}")

            # Create RL report
            hfss.post.create_report(
                expressions = expressions_for_RL,
                variations = variations,
                plot_name = f"RL_{var_label}"
            )

            # Export RL graphs as csv
            hfss.post.export_report_to_file(
                output_dir = csv_dir,
                plot_name = f"RL_{var_label}",
                extension = ".csv"
            )
            print(f"✅ Exported to CSV: {csv_dir}")

    # Save project
    hfss.save_project()




print(f"Project finished ✨")
