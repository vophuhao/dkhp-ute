import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
from datetime import datetime
import time


class CourseRegistrationTool:
    def __init__(self, root):
        self.root = root
        self.root.title("HCMUTE - Công cụ đăng ký học phần")
        self.root.geometry("700x550")
        self.stop_requested = False
        
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # JWT Token Section
        ttk.Label(main_frame, text="JWT Token:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.jwt_entry = scrolledtext.ScrolledText(main_frame, height=4, width=60, wrap=tk.WORD)
        self.jwt_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Course Information
        ttk.Label(main_frame, text="Mã lớp học phần (mỗi mã một dòng):", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(15, 5))
        
        self.schedule_alias_entry = scrolledtext.ScrolledText(main_frame, height=6, width=60, wrap=tk.WORD, font=('Arial', 10))
        self.schedule_alias_entry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.schedule_alias_entry.insert("1.0", "ADPL331379_03\n")
        
        # Register Button
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        self.register_btn = ttk.Button(button_frame, text="ĐĂNG KÝ MÔN HỌC", command=self.register_course, style='Accent.TButton')
        self.register_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="DỪNG LẠI", command=self.stop_registration, state='disabled')
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Response Section
        ttk.Label(main_frame, text="Kết quả:", font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky=tk.W, pady=(10, 5))
        self.response_text = scrolledtext.ScrolledText(main_frame, height=15, width=60, wrap=tk.WORD)
        self.response_text.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        main_frame.rowconfigure(6, weight=1)
    
    def stop_registration(self):
        """Stop the registration process"""
        self.stop_requested = True
        self.response_text.insert(tk.END, "\n⚠️ Đang dừng lại...\n")
        self.root.update()
    
    def register_course(self):
        """Send registration request to API"""
        # Get JWT token
        jwt_token = self.jwt_entry.get("1.0", tk.END).strip()
        if not jwt_token:
            messagebox.showerror("Lỗi", "Vui lòng nhập JWT Token!")
            return
        
        # Get course information (multiple courses, one per line)
        schedule_aliases_text = self.schedule_alias_entry.get("1.0", tk.END).strip()
        schedule_aliases = [line.strip() for line in schedule_aliases_text.split("\n") if line.strip()]
        
        # Validate required fields
        if not schedule_aliases:
            messagebox.showerror("Lỗi", "Vui lòng nhập ít nhất một ScheduleStudyUnitAlias!")
            return
        
        # Fixed API parameters
        turn_id = "66"
        study_program_id = "22110ST"
        action = "REGIST"
        
        # Prepare request URL and headers
        url = f"https://dangkyapi.hcmute.edu.vn/api/Regist/RegistScheduleStudyUnit?TurnID={turn_id}&Action={action}&StudyProgramID={study_program_id}"
        
        headers = {
            "host": "dangkyapi.hcmute.edu.vn",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://dkmh.hcmute.edu.vn/",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jwt_token}",
            "Origin": "https://dkmh.hcmute.edu.vn",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site"
        }
        
        # Reset stop flag and disable/enable buttons
        self.stop_requested = False
        self.register_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.response_text.delete('1.0', tk.END)
        self.response_text.insert('1.0', f"Đang đăng ký {len(schedule_aliases)} môn học...\n")
        self.response_text.insert(tk.END, "Chế độ: Tự động thử lại cho đến khi thành công\n\n")
        self.root.update()
        
        success_count = 0
        fail_count = 0
        
        try:
            # Process each course
            for idx, schedule_alias in enumerate(schedule_aliases, 1):
                if self.stop_requested:
                    self.response_text.insert(tk.END, f"\n⚠️ Đã dừng! Còn {len(schedule_aliases) - idx + 1} môn chưa đăng ký.\n")
                    break
                
                # Auto-generate other fields from ScheduleStudyUnitAlias
                curriculum_id = f"252{schedule_alias}"
                study_unit_id = schedule_alias.split("_")[0]
                if not study_unit_id.startswith("252"):
                    study_unit_id = f"252{study_unit_id}"
                
                # Prepare payload for this course
                payload = [{
                    "CurriculumID": curriculum_id,
                    "ScheduleStudyUnitAlias": schedule_alias,
                    "CurriculumName": "",
                    "StudyUnitID": study_unit_id,
                    "TypeName": "Lý thuyết",
                    "Credits": 0,
                    "StudyUnitTypeID": 1,
                    "IsRegisted": False
                }]
                
                # Retry until success
                self.response_text.insert(tk.END, f"[{idx}/{len(schedule_aliases)}] Đăng ký: {schedule_alias}\n")
                self.root.update()
                
                attempt = 0
                registered = False
                
                while not registered and not self.stop_requested:
                    attempt += 1
                    
                    try:
                        # Send request
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        self.response_text.insert(tk.END, f"  [{timestamp}] Lần thử #{attempt}... ")
                        self.root.update()
                        
                        response = requests.post(url, headers=headers, json=payload, timeout=30)
                        
                        if response.status_code == 200:
                            self.response_text.insert(tk.END, f"✓ THÀNH CÔNG!\n")
                            success_count += 1
                            registered = True
                            
                            try:
                                response_json = response.json()
                                self.response_text.insert(tk.END, f"  Response: {json.dumps(response_json, ensure_ascii=False)}\n")
                            except json.JSONDecodeError:
                                pass
                        else:
                            self.response_text.insert(tk.END, f"✗ (Status: {response.status_code})\n")
                        
                        self.root.update()
                        
                    except requests.exceptions.Timeout:
                        self.response_text.insert(tk.END, f"✗ Timeout\n")
                        
                    except requests.exceptions.RequestException as e:
                        self.response_text.insert(tk.END, f"✗ Lỗi\n")
                    
                    # Wait before retry if not successful
                    if not registered and not self.stop_requested:
                        time.sleep(1)  # Wait 1 second before retry
                
                if not registered:
                    fail_count += 1
                
                self.response_text.insert(tk.END, "\n")
                self.root.update()
            
            # Show summary
            summary = f"\n{'='*50}\nTổng kết:\n"
            summary += f"  - Thành công: {success_count}/{len(schedule_aliases)}\n"
            summary += f"  - Thất bại: {fail_count}/{len(schedule_aliases)}\n"
            self.response_text.insert(tk.END, summary)
            
            if fail_count == 0:
                messagebox.showinfo("Hoàn thành", f"Đăng ký thành công {success_count} môn học!")
            else:
                messagebox.showwarning("Hoàn thành", f"Thành công: {success_count}, Thất bại: {fail_count}")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
            self.response_text.insert(tk.END, f"\n\nLỗi hệ thống: {str(e)}")
            
        finally:
            self.register_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self.stop_requested = False


def main():
    root = tk.Tk()
    app = CourseRegistrationTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
