import tkinter as tk
import time
from threading import Thread
from pygame import mixer
import os
import json
from tkinter import ttk 

class PomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 포모도로 타이머")
        self.root.geometry("1050x650") 
        self.is_running = False
        self.timer_thread = None
        self.alarm_thread = None
        self.stop_alarm_flag = False
        self.alarm_playing = False
        self.todos = {}
        self.current_selected_todo = "" 

        mixer.init()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.alarm_path = os.path.join(self.base_dir, "alarm.mp3")
        self.todo_file = os.path.join(self.base_dir, "todos.json")

        # --- Notion 스타일 ttk Style 설정 ---
        self.style = ttk.Style()
        self.style.theme_use('clam') 

        # Notion과 유사한 중성적이고 부드러운 색상 팔레트
        # 이 변수들을 'self.'를 사용하여 인스턴스 변수로 정의합니다.
        self.notion_bg_light = "#FFFFFF"     # 흰색에 가까운 배경
        self.notion_bg_medium = "#F7F7F7"    # 약간 회색빛 도는 배경 (프레임 등)
        self.notion_bg_dark = "#EDEDED"      # 더 진한 회색 (구분선 느낌)
        self.notion_text = "#333333"         # 진한 회색 텍스트
        self.notion_subtext = "#808080"      # 서브 텍스트 (힌트, 상태 등)
        self.notion_primary = "#2F80ED"      # 주요 액션 색상 (파란색)
        self.notion_primary_hover = "#5D9CEC" # 주요 액션 호버 색상
        self.notion_alert = "#EB5757"        # 알람/경고 색상 (빨간색)
        self.notion_alert_hover = "#F27878"  # 알람 호버 색상
        self.notion_border = "#E0E0E0"       # 옅은 테두리 색상

        # self.root.configure(bg=notion_bg_light) 대신 self.notion_bg_light 사용
        self.root.configure(bg=self.notion_bg_light) 

        # TFrame 스타일 - 테두리 없이 플랫하게
        self.style.configure('TFrame', background=self.notion_bg_light)
        self.style.configure('OuterFrame.TFrame', background=self.notion_bg_medium, relief="flat", borderwidth=0)

        self.style.configure('TLabelframe', background=self.notion_bg_medium, foreground=self.notion_text, borderwidth=0, relief="flat")
        self.style.configure('TLabelframe.Label', background=self.notion_bg_medium, foreground=self.notion_text, font=("Arial", 11, "bold")) 

        # TLabel 스타일
        self.style.configure('TLabel', background=self.notion_bg_light, foreground=self.notion_text, font=("Arial", 10))
        self.style.configure('Timer.TLabel', background=self.notion_bg_medium, foreground=self.notion_text) 
        self.style.configure('TodoItem.TLabel', background=self.notion_bg_medium, foreground=self.notion_text) 
        self.style.configure('Message.TLabel', background=self.notion_bg_light, foreground=self.notion_subtext, font=("Arial", 12)) 

        # TButton 스타일 - 플랫하고 미니멀하게
        self.style.configure('TButton', font=('Arial', 10, 'bold'), background=self.notion_primary, foreground='white', relief="flat", borderwidth=0)
        self.style.map('TButton',
                       background=[('active', self.notion_primary_hover)],
                       foreground=[('active', 'white')]) 

        # Stop Alarm Button 스타일
        self.style.configure('Alarm.TButton', background=self.notion_alert, foreground='white', relief="flat", borderwidth=0)
        self.style.map('Alarm.TButton',
                       background=[('active', self.notion_alert_hover)], 
                       foreground=[('active', 'white')])

        # TEntry 스타일 - 얇은 테두리와 깔끔한 배경
        self.style.configure('TEntry', fieldbackground="white", foreground=self.notion_text, borderwidth=1, relief="solid", focusthickness=1, focuscolor=self.notion_primary)
        
        # TCheckbutton 스타일
        self.style.configure('TCheckbutton', background=self.notion_bg_medium, foreground=self.notion_text, indicatoron=True, borderwidth=0) 
        self.style.map('TCheckbutton',
                       background=[('active', self.notion_bg_medium)], 
                       foreground=[('selected', self.notion_primary)], 
                       indicatorcolor=[('selected', self.notion_primary)]) 

        # TScrollbar 스타일
        self.style.configure('Vertical.TScrollbar', background=self.notion_bg_light, troughcolor=self.notion_bg_light, relief="flat", borderwidth=0)
        self.style.map('Vertical.TScrollbar',
                       background=[('active', self.notion_bg_dark)], 
                       troughcolor=[('active', self.notion_bg_light)])

        # --- 메인 프레임 설정 ---
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20) 

        self.timer_frame = ttk.Frame(self.main_frame, style='OuterFrame.TFrame', borderwidth=1, relief="solid", cursor="arrow") 
        self.timer_frame.pack(side="left", fill="y", padx=(0, 10), pady=0) 

        self.todo_frame = ttk.Frame(self.main_frame, style='OuterFrame.TFrame', borderwidth=1, relief="solid", cursor="arrow") 
        self.todo_frame.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=0) 

        # --- 타이머 UI ---
        ttk.Label(self.timer_frame, text="🧠 공부 시간", style='Timer.TLabel', font=("Arial", 13, "bold")).pack(pady=(20, 5))
        study_frame = ttk.Frame(self.timer_frame) 
        study_frame.pack()
        self.study_min = ttk.Entry(study_frame, width=5); self.study_min.insert(0, "25")
        self.study_min.pack(side="left")
        ttk.Label(study_frame, text="분", style='TLabel').pack(side="left", padx=(0, 10)) 
        self.study_sec = ttk.Entry(study_frame, width=5); self.study_sec.insert(0, "00")
        self.study_sec.pack(side="left")
        ttk.Label(study_frame, text="초", style='TLabel').pack(side="left") 

        ttk.Label(self.timer_frame, text="🛌 휴식 시간", style='Timer.TLabel', font=("Arial", 13, "bold")).pack(pady=(15, 5))
        break_frame = ttk.Frame(self.timer_frame) 
        break_frame.pack()
        self.break_min = ttk.Entry(break_frame, width=5); self.break_min.insert(0, "5")
        self.break_min.pack(side="left")
        ttk.Label(break_frame, text="분", style='TLabel').pack(side="left", padx=(0, 10)) 
        self.break_sec = ttk.Entry(break_frame, width=5); self.break_sec.insert(0, "00")
        self.break_sec.pack(side="left")
        ttk.Label(break_frame, text="초", style='TLabel').pack(side="left") 

        # tk.Label의 bg와 fg도 self.notion_bg_medium, self.notion_text 사용
        self.label = tk.Label(self.timer_frame, text="00:00", font=("Helvetica Neue", 48, "bold"), bg=self.notion_bg_medium, fg=self.notion_text)
        self.label.pack(pady=30)

        self.stop_alarm_btn = ttk.Button(self.timer_frame, text="🔕 알람 끄기", command=self.stop_alarm, style='Alarm.TButton')
        self.stop_alarm_btn.pack(pady=(0, 10))
        self.stop_alarm_btn.config(state="disabled")

        button_row_frame = ttk.Frame(self.timer_frame)
        button_row_frame.pack(pady=(0, 20)) 

        self.start_btn = ttk.Button(button_row_frame, text="▶ 시작", command=self.start_timer)
        self.start_btn.pack(side="left", padx=(0, 10), pady=0) 
        self.reset_btn = ttk.Button(button_row_frame, text="⏹ 중지", command=self.stop_timer)
        self.reset_btn.pack(side="left", padx=(10, 0), pady=0) 

        self.message = ttk.Label(self.timer_frame, text="", style='Message.TLabel')
        self.message.pack(pady=(0, 10))
        
        self.current_todo_label = ttk.Label(self.timer_frame, text="현재 할 일: 없음", font=("Arial", 11, "italic"), foreground=self.notion_subtext, style='Message.TLabel')
        self.current_todo_label.pack(pady=(0, 20))


        # --- To-Do 리스트 UI ---
        ttk.Label(self.todo_frame, text="📝 일주일 할 일", font=("Arial", 16, "bold"), style='TLabel').pack(pady=(20, 10))
        
        self.days = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
        self.new_todo_entries = {} 
        self.todo_list_frames = {} 

        # tk.Canvas의 bg와 highlightbackground도 self.notion_bg_medium 사용
        self.todo_canvas = tk.Canvas(self.todo_frame, bg=self.notion_bg_medium, highlightbackground=self.notion_bg_medium, highlightthickness=0) 
        self.todo_canvas.pack(side="left", fill="both", expand=True)

        self.todo_scrollbar = ttk.Scrollbar(self.todo_frame, orient="vertical", command=self.todo_canvas.yview, style='Vertical.TScrollbar')
        self.todo_scrollbar.pack(side="right", fill="y")

        self.todo_canvas.configure(yscrollcommand=self.todo_scrollbar.set)
        self.todo_canvas.bind('<Configure>', lambda e: self.todo_canvas.configure(scrollregion = self.todo_canvas.bbox("all")))
        
        self.todo_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.todo_canvas.bind_all("<Button-4>", self._on_mousewheel) 
        self.todo_canvas.bind_all("<Button-5>", self._on_mousewheel) 

        self.inner_todo_frame = ttk.Frame(self.todo_canvas, style='OuterFrame.TFrame') 
        self.todo_canvas.create_window((0, 0), window=self.inner_todo_frame, anchor="nw")

        for day in self.days:
            day_section_frame = ttk.LabelFrame(self.inner_todo_frame, text=day, style='TLabelframe') 
            day_section_frame.pack(fill="x", padx=10, pady=(10, 5), expand=True) 

            add_todo_frame = ttk.Frame(day_section_frame) 
            add_todo_frame.pack(fill="x", pady=(5, 10), padx=5) 
            
            ttk.Label(add_todo_frame, text="새 할 일:", style='TLabel').pack(side="left", padx=(0, 5)) 
            entry = ttk.Entry(add_todo_frame, width=25) 
            entry.pack(side="left", fill="x", expand=True, padx=(0, 5)) 
            self.new_todo_entries[day] = entry
            
            add_btn = ttk.Button(add_todo_frame, text="추가", command=lambda d=day: self.add_todo(d))
            add_btn.pack(side="left")
            
            todo_list_frame = ttk.Frame(day_section_frame, style='OuterFrame.TFrame', relief="flat", borderwidth=0) 
            todo_list_frame.pack(fill="x", pady=(0, 5), padx=5) 
            self.todo_list_frames[day] = todo_list_frame

            if day != self.days[-1]: 
                # ttk.Separator의 background도 self.notion_border 사용
                ttk.Separator(self.inner_todo_frame, orient='horizontal', style='HSeparator.TSeparator').pack(fill='x', padx=10, pady=(5, 15))

        # Separator 스타일 추가
        self.style.configure('HSeparator.TSeparator', background=self.notion_border)

        button_frame = ttk.Frame(self.todo_frame) 
        button_frame.pack(pady=(10, 20)) 
        ttk.Button(button_frame, text="모든 할 일 저장하기", command=self.save_all_todos).pack(side="left", padx=10)
        ttk.Button(button_frame, text="전체 초기화", command=self.clear_all_todos).pack(side="left", padx=10)


        # --- 초기화 및 종료 설정 ---
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.load_todos() 
        self.update_all_todo_displays() 

    # --- 마우스 휠 스크롤 핸들러 ---
    def _on_mousewheel(self, event):
        if event.delta: 
            self.todo_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif event.num == 4: 
            self.todo_canvas.yview_scroll(-1, "units")
        elif event.num == 5: 
            self.todo_canvas.yview_scroll(1, "units")

    # --- To-Do 리스트 관련 메서드 ---
    def load_todos(self):
        self.todos = {day: [] for day in self.days} 

        if os.path.exists(self.todo_file):
            try:
                with open(self.todo_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    for day in self.days:
                        if day in loaded_data and isinstance(loaded_data[day], list):
                            for item in loaded_data[day]:
                                if isinstance(item, dict) and 'text' in item and 'completed' in item:
                                    self.todos[day].append(item)
                                elif isinstance(item, str): 
                                    self.todos[day].append({'text': item, 'completed': False})
            except Exception as e:
                print(f"To-Do 불러오기 오류: {e}. 기존 데이터는 유지하고, 파일 로드 실패로 인한 문제는 무시합니다.")


    def save_all_todos(self):
        try:
            with open(self.todo_file, 'w', encoding='utf-8') as f:
                json.dump(self.todos, f, ensure_ascii=False, indent=4)
            print("모든 To-Do가 저장되었습니다.")
        except Exception as e:
            print(f"To-Do 저장 오류: {e}")

    def add_todo(self, day):
        new_todo_text = self.new_todo_entries[day].get().strip()
        if new_todo_text:
            self.todos[day].append({'text': new_todo_text, 'completed': False})
            self.new_todo_entries[day].delete(0, tk.END) 
            self.update_todo_display(day)
            self.save_all_todos()
        else:
            tk.messagebox.showwarning("입력 오류", "할 일 내용을 입력해주세요.")

    def delete_todo(self, day, index):
        if day in self.todos and 0 <= index < len(self.todos[day]):
            del self.todos[day][index]
            self.update_todo_display(day)
            self.save_all_todos()

    def toggle_todo_completed(self, day, index):
        if day in self.todos and 0 <= index < len(self.todos[day]):
            self.todos[day][index]['completed'] = not self.todos[day][index]['completed']
            self.update_todo_display(day) 
            self.save_all_todos() 

    def select_current_todo(self, todo_text):
        self.current_selected_todo = todo_text
        self.root.after(0, self.current_todo_label.config, {'text': f"현재 할 일: {todo_text}"})
        print(f"현재 할 일이 '{todo_text}'(으)로 설정되었습니다.")

    def update_todo_display(self, day):
        for widget in self.todo_list_frames[day].winfo_children():
            widget.destroy()

        if day in self.todos: 
            for index, todo_item in enumerate(self.todos[day]):
                item_frame = ttk.Frame(self.todo_list_frames[day], style='OuterFrame.TFrame') 
                item_frame.pack(fill="x", pady=2, padx=5) 

                completed_var = tk.BooleanVar(value=todo_item['completed'])
                check_btn = ttk.Checkbutton(item_frame, variable=completed_var,
                                           command=lambda d=day, i=index: self.toggle_todo_completed(d, i), style='TCheckbutton')
                check_btn.pack(side="left", padx=(0, 5)) 

                font_style = ("Arial", 10) 
                if todo_item['completed']:
                    font_style = ("Arial", 10, "overstrike") 
                
                # 'self.' 접두사를 사용하여 인스턴스 변수에 접근합니다.
                text_color = self.notion_subtext if todo_item['completed'] else self.notion_text

                todo_label = tk.Label(item_frame, text=todo_item['text'], font=font_style, anchor="w",
                                      bg=self.style.lookup('TodoItem.TLabel', 'background'), 
                                      fg=text_color) 
                todo_label.pack(side="left", fill="x", expand=True)

                delete_btn = ttk.Button(item_frame, text="❌", command=lambda d=day, i=index: self.delete_todo(d, i), width=3)
                delete_btn.pack(side="right")

                select_btn = ttk.Button(item_frame, text="선택", command=lambda t=todo_item['text']: self.select_current_todo(t), width=4)
                select_btn.pack(side="right", padx=(0, 5))

        self.root.after(100, lambda: self.todo_canvas.configure(scrollregion=self.todo_canvas.bbox("all")))


    def update_all_todo_displays(self):
        for day in self.days:
            self.update_todo_display(day)
        self.root.after(100, lambda: self.todo_canvas.configure(scrollregion=self.todo_canvas.bbox("all")))

    def clear_all_todos(self):
        for day in self.days:
            self.new_todo_entries[day].delete(0, tk.END)
            self.todos[day] = [] 
            self.update_todo_display(day) 
        self.save_all_todos()
        self.select_current_todo("없음")

    # --- 기존 타이머 관련 메서드 (변경 없음) ---
    def _on_closing(self):
        self.save_all_todos()
        self.stop_timer()
        mixer.quit()
        self.root.destroy()

    def countdown(self, seconds, on_end_callback):
        while seconds > 0 and self.is_running:
            mins, secs = divmod(seconds, 60)
            self.root.after(0, self.label.config, {'text': f"{mins:02}:{secs:02}"})
            time.sleep(1)
            seconds -= 1

        if self.is_running:
            self.root.after(0, self.play_alarm)
            self.root.after(0, on_end_callback)
        else:
            self.root.after(0, self.label.config, {'text': "00:00"})
            self.root.after(0, self.message.config, {'text': ""})

    def play_alarm(self):
        if self.alarm_playing:
            return

        self.stop_alarm_flag = False
        self.alarm_playing = True
        self.root.after(0, self.stop_alarm_btn.config, {'state': "normal"})
        
        def alarm_loop():
            try:
                mixer.music.load(self.alarm_path)
                mixer.music.play(-1)

                while not self.stop_alarm_flag:
                    time.sleep(0.1)

            except Exception as e:
                print(f"알람 재생 오류: {e}")
            finally:
                if mixer.music.get_busy():
                    mixer.music.stop()
                self.alarm_playing = False
                self.root.after(0, self.stop_alarm_btn.config, {'state': "disabled"})

        self.alarm_thread = Thread(target=alarm_loop, daemon=True)
        self.alarm_thread.start()

    def stop_alarm(self):
        self.stop_alarm_flag = True
        self.root.after(0, self.stop_alarm_btn.config, {'state': "disabled"})

    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            display_message = ""
            if self.current_selected_todo and self.current_selected_todo != "없음":
                display_message = f"📚 공부 시작! ({self.current_selected_todo})"
            else:
                display_message = "📚 공부 시작!"
            self.root.after(0, self.message.config, {'text': display_message})
            self.start_focus()

    def start_focus(self):
        try:
            minutes = int(self.study_min.get())
            seconds = int(self.study_sec.get())
            total_seconds = minutes * 60 + seconds
            self.timer_thread = Thread(target=self.countdown, args=(total_seconds, self.focus_done), daemon=True)
            self.timer_thread.start()
        except ValueError:
            self.root.after(0, self.label.config, {'text': "잘못된 시간 입력"})

    def focus_done(self):
        self.root.after(0, self.message.config, {'text': "✅ 공부 완료! 알람을 끄면 휴식 시작"})
        
        def wait_then_break():
            while self.is_running and not self.stop_alarm_flag:
                time.sleep(0.2)
            if self.is_running:
                self.root.after(0, self.start_break)

        Thread(target=wait_then_break, daemon=True).start()

    def start_break(self):
        try:
            minutes = int(self.break_min.get())
            seconds = int(self.break_sec.get())
            total_seconds = minutes * 60 + seconds
            self.root.after(0, self.message.config, {'text': "💤 휴식 시작!"})
            self.timer_thread = Thread(target=self.countdown, args=(total_seconds, self.break_done), daemon=True)
            self.timer_thread.start()
        except ValueError:
            self.root.after(0, self.label.config, {'text': "잘못된 시간 입력"})

    def break_done(self):
        self.root.after(0, self.message.config, {'text': "📢 휴식 완료! 알람을 끄면 다시 공부 시작!"})
        self.root.after(0, self.play_alarm)

        def wait_then_focus():
            while self.is_running and not self.stop_alarm_flag:
                time.sleep(0.2)
            
            if self.is_running and self.stop_alarm_flag:
                self.root.after(0, self.start_focus)
        
        Thread(target=wait_then_focus, daemon=True).start()

    def stop_timer(self):
        self.is_running = False
        self.stop_alarm()
        self.root.after(0, self.label.config, {'text': "00:00"})
        self.root.after(0, self.message.config, {'text': ""})
        self.root.after(0, self.stop_alarm_btn.config, {'state': "disabled"})

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()