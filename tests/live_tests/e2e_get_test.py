from simplybookapi.main import Main

m = Main(test_mode=False)

res = m.get('admin','getEventList')

a = 0