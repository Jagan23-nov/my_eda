from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)
workspace = "../workspace"
results = "../results"

@app.route("/compile", methods=["POST"])
def compile_code():
    data = request.json
    design_code = data.get("design", "")
    tb_code = data.get("testbench", "")

    design_path = os.path.join(workspace, "design.sv")      # Supports SystemVerilog
    tb_path = os.path.join(workspace, "testbench.cpp")

    with open(design_path, "w") as f:
        f.write(design_code)

    with open(tb_path, "w") as f:
        f.write(tb_code)

    try:
        # Use --sv to enable SystemVerilog support
        verilator_cmd = f"verilator --cc --sv {design_path} --exe {tb_path}"
        subprocess.run(verilator_cmd, shell=True, check=True, cwd=results)

        make_cmd = "make -C obj_dir -f Vdesign.mk Vdesign"
        subprocess.run(make_cmd, shell=True, check=True, cwd=results)

        return jsonify({ "output": "✅ Compilation successful (Verilog/SystemVerilog supported)" })

    except subprocess.CalledProcessError as e:
        return jsonify({ "error": str(e) })

@app.route("/run", methods=["GET"])
def run_simulation():
    try:
        sim_cmd = "./obj_dir/Vdesign"
        output = subprocess.check_output(sim_cmd, shell=True, cwd=results, text=True)
        return jsonify({ "output": output })
    except subprocess.CalledProcessError as e:
        return jsonify({ "error": str(e) })

if __name__ == "__main__":
    app.run(debug=True)

