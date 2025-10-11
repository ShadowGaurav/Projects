#Made by Shadow
import tkinter as tk
from tkinter import font as tkfont
import math

class GradientCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Gradient Calculator")
        self.root.geometry("400x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")
        
        self.expression = ""
        self.result_var = tk.StringVar()
        self.result_var.set("0")
        
        # Custom fonts
        self.display_font = tkfont.Font(family="Helvetica", size=32, weight="bold")
        self.button_font = tkfont.Font(family="Helvetica", size=18, weight="bold")
        self.small_font = tkfont.Font(family="Helvetica", size=12)
        
        self.create_ui()
        
    def create_ui(self):
        # Display frame with gradient effect
        display_frame = tk.Frame(self.root, bg="#16213e", height=150)
        display_frame.pack(fill="both", padx=10, pady=10)
        display_frame.pack_propagate(False)
        
        # Expression label (shows what you're typing)
        self.expr_label = tk.Label(
            display_frame, 
            text="", 
            font=self.small_font,
            bg="#16213e", 
            fg="#94a3b8",
            anchor="e",
            padx=20
        )
        self.expr_label.pack(fill="x", pady=(20, 5))
        
        # Result display
        result_display = tk.Label(
            display_frame,
            textvariable=self.result_var,
            font=self.display_font,
            bg="#16213e",
            fg="#ffffff",
            anchor="e",
            padx=20
        )
        result_display.pack(fill="both", expand=True)
        
        # Buttons frame
        buttons_frame = tk.Frame(self.root, bg="#1a1a2e")
        buttons_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Button layout
        buttons = [
            ['C', '⌫', '%', '/'],
            ['7', '8', '9', 'x'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['±', '0', '.', '=']
        ]
        
        # Color schemes for different button types
        colors = {
            'number': {'bg': '#2d3561', 'fg': '#ffffff', 'active': '#3d4575'},
            'operator': {'bg': '#0f3460', 'fg': '#e94560', 'active': '#1a4470'},
            'function': {'bg': '#533483', 'fg': '#ffffff', 'active': '#643593'},
            'equals': {'bg': '#e94560', 'fg': '#ffffff', 'active': '#f55570'}
        }
        
        for i, row in enumerate(buttons):
            for j, btn_text in enumerate(row):
                # Determine button type and color
                if btn_text in ['C', '⌫', '%', '±']:
                    btn_color = colors['function']
                elif btn_text in ['/', 'x', '-', '+']:
                    btn_color = colors['operator']
                elif btn_text == '=':
                    btn_color = colors['equals']
                else:
                    btn_color = colors['number']
                
                btn = tk.Button(
                    buttons_frame,
                    text=btn_text,
                    font=self.button_font,
                    bg=btn_color['bg'],
                    fg=btn_color['fg'],
                    activebackground=btn_color['active'],
                    activeforeground=btn_color['fg'],
                    bd=0,
                    cursor="hand2",
                    command=lambda x=btn_text: self.on_button_click(x)
                )
                btn.grid(row=i, column=j, sticky="nsew", padx=5, pady=5)
                
                # Hover effect
                btn.bind("<Enter>", lambda e, b=btn, c=btn_color: 
                        b.config(bg=c['active']))
                btn.bind("<Leave>", lambda e, b=btn, c=btn_color: 
                        b.config(bg=c['bg']))
        
        # Configure grid weights for responsive sizing
        for i in range(5):
            buttons_frame.grid_rowconfigure(i, weight=1)
        for j in range(4):
            buttons_frame.grid_columnconfigure(j, weight=1)
    
    def on_button_click(self, char):
        if char == 'C':
            self.expression = ""
            self.result_var.set("0")
            self.expr_label.config(text="")
            
        elif char == '⌫':
            self.expression = self.expression[:-1]
            self.expr_label.config(text=self.expression)
            if not self.expression:
                self.result_var.set("0")
                
        elif char == '=':
            try:
                # Replace x with * for calculation
                calc_expr = self.expression.replace('x', '*')
                result = eval(calc_expr)
                
                # Format result
                if isinstance(result, float):
                    if result.is_integer():
                        result = int(result)
                    else:
                        result = round(result, 8)
                
                self.result_var.set(str(result))
                self.expression = str(result)
                self.expr_label.config(text="")
            except:
                self.result_var.set("Error")
                self.expression = ""
                
        elif char == '±':
            if self.expression and self.expression[0] == '-':
                self.expression = self.expression[1:]
            elif self.expression:
                self.expression = '-' + self.expression
            self.expr_label.config(text=self.expression)
            
        elif char == '%':
            try:
                result = float(self.expression) / 100
                self.expression = str(result)
                self.result_var.set(self.expression)
                self.expr_label.config(text="")
            except:
                pass
                
        else:
            # Add character to expression
            if char == 'x':
                self.expression += 'x'
            else:
                self.expression += char
            self.expr_label.config(text=self.expression)
            
            # Live preview calculation
            try:
                if char not in ['+', '-', 'x', '/', '.']:
                    calc_expr = self.expression.replace('x', '*')
                    result = eval(calc_expr)
                    if isinstance(result, float):
                        if result.is_integer():
                            result = int(result)
                        else:
                            result = round(result, 8)
                    self.result_var.set(str(result))
            except:
                pass

if __name__ == "__main__":
    root = tk.Tk()
    app = GradientCalculator(root)
    root.mainloop()