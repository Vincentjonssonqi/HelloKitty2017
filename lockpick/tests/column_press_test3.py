import lockpick as l
import time
a = l.Lockpick()
#a.press_columns()
print(a.press_key(0,0,True))
time.sleep(1)
print(a.press_key(0,0,True))
time.sleep(1)
print(a.press_key(0,0,True))
time.sleep(5)


print(a.press_key(1,0,True))
time.sleep(1)
print(a.press_key(1,1,True))
time.sleep(1)
print(a.press_key(1,2,True))
time.sleep(5)


print(a.press_key(2,0,True))
time.sleep(1)
print(a.press_key(2,1,True))
time.sleep(1)
print(a.press_key(2,2,True))
time.sleep(5)

print(a.press_key(3,0,True))
time.sleep(1)
print(a.press_key(3,1,True))
time.sleep(1)
print(a.press_key(3,2,True))
