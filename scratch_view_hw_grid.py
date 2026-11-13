with open('web/src/components/HardwareStatusGrid.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('setCalibratingDevice(dev.code)')
print(text[idx-300:idx+400])
