print("Nhap cac dong tu van ban(Nhap'code' de ket thuc:)")
lines =[]
while True:
    line =input ()
    if line.lower() == 'done':
       break
    lines.append(line)
print("\n Cac dong da nhap sau khi chuy nhanh in hoa :")
for line in lines:
    print(line.upper())