from textwrap import wrap
from tkinter import *
from random import *
from tkinter import messagebox


def create_entries():
    nums = S_Entry.get()

    if nums.isdigit() != True:
        messagebox.showerror("Ошибка", "Пожалуйста, введите сумматор как число.")
        return
    elif int(nums) > 3 or int(nums) < 1:
        messagebox.showerror("Ошибка", "Пожалуйста, введите кол-во сумматоров от 1 до 3.")
        return

    entry_list = []
    nums = int(S_Entry.get())
    for i in range(nums):
        entry_label = Label(window, text=f"Сумматор {i+1}: . Пример: 123")
        entry_label.pack()
        entry = Entry(window)
        entry.pack()
        entry_list.append(entry)

    run_button = Button(window, text="Запуск", command=lambda: run(entry_list))
    run_button.pack()

def decode(code_str, summators, nums):
    encoded_symbols = [int(bit) for bit in code_str]

    # Инициализация параметров
    nums_of_states = 2 ** nums
    state_metric = [float('inf')] * nums_of_states
    state_metric[0] = 0  # Начальное состояние (все регистры равны нулю)
    path = [[] for _ in range(nums_of_states)]

    # Функция для вычисления выхода сверточного кодера
    def convolutional_output(state, input_bit):
        output = []
        state_bits = [(state >> i) & 1 for i in range(nums)]
        for reg in summators:
            output_bit = input_bit
            for bit, r in zip(state_bits, reg[1:]):
                output_bit ^= bit * r
            output.append(output_bit)
        return output

    # Основной цикл алгоритма Витерби
    for i in range(0, len(encoded_symbols), len(summators)):
        received_bits = encoded_symbols[i:i + len(summators)]
        new_state_metric = [float('inf')] * nums_of_states
        new_path = [[] for _ in range(nums_of_states)]

        for state in range(nums_of_states):
            for input_bit in [0, 1]:
                next_state = ((state << 1) | input_bit) & (nums_of_states - 1)
                output_bits = convolutional_output(state, input_bit)
                hamming_dist = sum([rb ^ ob for rb, ob in zip(received_bits, output_bits)])

                metric = state_metric[state] + hamming_dist
                if metric < new_state_metric[next_state]:
                    new_state_metric[next_state] = metric
                    new_path[next_state] = path[state] + [input_bit]

        state_metric = new_state_metric
        path = new_path

    # Найти путь с минимальной метрикой
    min_metric_number = state_metric.index(min(state_metric))
    decode_str = path[min_metric_number]
    return decode_str

def run(entry_list):
    window_c = Tk()
    window_c.title("Процесс кодирования")
    window_c.geometry("400x400")

    rule = []
    b = []
    K = int(K_Entry.get())
    S = int(S_Entry.get())
    for entry in entry_list:
        data = entry.get()
        if data == '':
            messagebox.showerror("Ошибка", "Пожалуйста, введите сумматор.")
            window_c.destroy()
            return
        elif data.isdigit() != True:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректно сумматор.")
            window_c.destroy()
            return
        rule.append(data)
    text = str(text_entry.get())
    if text == "":
        messagebox.showerror("Ошибка", "Пожалуйста, введите текст.")
        window_c.destroy()
        return

    text_to_binary = "".join(format(x, "08b") for x in bytearray(text, "utf-8"))

    text_info_a = Label(window_c, text='Двоичное представление')
    text_info_a.grid(row=0, column=0)
    out_window_a = Text(window_c, width=40, height=12)
    out_window_a.grid(row=1, column=0)
    out_window_a.insert(END, text_to_binary)
    out_window_a.config(state='disabled')

    c = text_to_binary
    a = list(map(int, c))

    for i in range(S):
        b.append([0]*K)
    for i in range(len(b)):
        for j in range(K):
            if str(j+1) in rule[i]:
                b[i][j] = 1

    text_info_b = Label(window_c, text='Таблица сумматоров по битам')
    text_info_b.grid(row=2, column=0)
    out_window_b = Text(window_c, width=40, height=12)
    out_window_b.grid(row=3, column=0)
    for i in range(len(b)):
        out_window_b.insert(END, b[i])
        out_window_b.insert(END, "\n")
    out_window_b.config(state='disabled')

    registers = [0] * K
    output_data = []
    output_word = []
    output_bitword = []

    for bit in a:
        registers.insert(0, bit)
        registers.pop()
        for i in range(len(b)):
            for j in range(len(registers)):
                if b[i][j] == 1:
                    out_bit = registers[j]
                    output_data.append((out_bit))
            k = 0
            for i in range(len(output_data)):
                k += output_data[i]
            output_data = []
            k = k % 2
            output_word.append(k)
            k = 0
        output_bitword.append(output_word)
        output_word = []

    code_str = ''
    for i in range(len(output_bitword)):
        for j in range(len(output_bitword[i])):
            code_str += ''.join(str(output_bitword[i][j]))
    decode_str = decode(code_str, b, K)

    d_to_utf = ''
    for i in range(len(decode_str)):
        d_to_utf += ''.join(str(decode_str[i]))
    d_str = int(d_to_utf, 2).to_bytes((len(d_to_utf) + 7) // 8, byteorder='big').decode('utf-8')

    text_info_c = Label(window_c, text='Таблица закодированных символов')
    text_info_c.grid(row=0, column=1)
    out_window_c = Text(window_c, width=40, height=12)
    out_window_c.grid(row=1, column=1)
    for i in range(len(output_bitword)):
        out_window_c.insert(END, output_bitword[i])
        out_window_c.insert(END, "\n")
    out_window_c.config(state='disabled')

    text_info_d = Label(window_c, text='Декодированные символы')
    text_info_d.grid(row=2, column=1)
    out_window_d = Text(window_c, width=40, height=12)
    out_window_d.grid(row=3, column=1)
    out_window_d.insert(END, decode_str)
    out_window_d.config(state='disabled')

    text_info_e = Label(window_c, text='Декодированная строка')
    text_info_e.grid(row=0, column=2)
    out_window_e = Text(window_c, width=40, height=12)
    out_window_e.grid(row=1, column=2)
    out_window_e.insert(END, d_str)
    out_window_e.config(state='disabled')

window = Tk()
window.title("Сверточные коды")
window.geometry("400x400")

text_label = Label(window, text="Введите текст:")
text_label.pack()

text_entry = Entry(window)
text_entry.pack()

K_label = Label(window, text='Введите количество регистров: ')
K_label.pack()

K_Entry = Entry(window)
K_Entry.pack()

S_label = Label(window, text='Введите количество сумматоров: ')
S_label.pack()

S_Entry = Entry(window)
S_Entry.pack()

create_button = Button(window, text="Введите сумматоры", command=create_entries)
create_button.pack()

window.mainloop()