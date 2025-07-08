import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import subprocess
import os

def save_file(content, filename):
    with open(filename, "w") as f:
        f.write(content)

def compile_and_simulate():
    design_code = design_editor.get("1.0", tk.END)
    tb_code = tb_editor.get("1.0", tk.END)

    save_file(design_code, "design.v")
    save_file(tb_code, "testbench.v")

    # Compile using iverilog
    try:
        subprocess.run(["iverilog", "-o", "output.vvp", "design.v", "testbench.v"], check=True)
        messagebox.showinfo("Compile Success", "Compilation successful. Running simulation...")

        # Simulate using vvp
        subprocess.run(["vvp", "output.vvp"], check=True)
        messagebox.showinfo("Simulation Done", "Simulation complete.")

        # Check VCD
        if os.path.exists("dump.vcd"):
            with open("dump.vcd", "r") as f:
                lines = f.readlines()
                vcd_view.delete("1.0", tk.END)
                vcd_view.insert(tk.END, "".join(lines[:50]))  # show first 50 lines
        else:
            messagebox.showwarning("VCD Missing", "No dump.vcd found. Make sure your testbench includes $dumpfile.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error during compilation or simulation:\n{e}")

def open_gtkwave():
    if os.path.exists("dump.vcd"):
        subprocess.Popen(["gtkwave", "dump.vcd"])
    else:
        messagebox.showwarning("VCD Missing", "Cannot open GTKWave. 'dump.vcd' not found.")

# === GUI Setup ===
root = tk.Tk()
root.title("Verilog HDL Editor & Simulator with GTKWave")

# === Design Code Frame ===
design_frame = tk.LabelFrame(root, text="Design Code (design.v)")
design_frame.pack(fill="both", expand=True, padx=10, pady=5)
design_editor = ScrolledText(design_frame, height=10)
design_editor.pack(fill="both", expand=True)

# === Testbench Code Frame ===
tb_frame = tk.LabelFrame(root, text="Testbench Code (testbench.v)")
tb_frame.pack(fill="both", expand=True, padx=10, pady=5)
tb_editor = ScrolledText(tb_frame, height=10)
tb_editor.pack(fill="both", expand=True)

# === GTKWave Preview Frame ===
vcd_frame = tk.LabelFrame(root, text="VCD File Preview (dump.vcd)")
vcd_frame.pack(fill="both", expand=True, padx=10, pady=5)
vcd_view = ScrolledText(vcd_frame, height=10)
vcd_view.pack(fill="both", expand=True)

# === Buttons ===
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)
save_button = tk.Button(btn_frame, text="💾 Save + Compile + Run", command=compile_and_simulate)
save_button.grid(row=0, column=0, padx=5)
gtkwave_button = tk.Button(btn_frame, text="📈 Open GTKWave", command=open_gtkwave)
gtkwave_button.grid(row=0, column=1, padx=5)

# === Sample Code Inserts ===
design_editor.insert(tk.END, """// Sample Verilog Design
module design(input a, b, output y);
    assign y = a & b;
endmodule
""")

tb_editor.insert(tk.END, """// Sample Testbench
module testbench;
    reg a, b;
    wire y;

    design dut(.a(a), .b(b), .y(y));

    initial begin
        $dumpfile("dump.vcd");
        $dumpvars(0, testbench);

        a = 0; b = 0;
        #10 a = 0; b = 1;
        #10 a = 1; b = 0;
        #10 a = 1; b = 1;
        #10 $finish;
    end
endmodule
""")

root.mainloop()

