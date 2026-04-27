CC = clang
CFLAGS = -O3 -march=native -Wall -s -ffast-math -flto=thin
SRCS = main.c eng.c analyze.c stats.c conf.c
PREFIX = /usr/local/
TARGET = gpugov

all: $(TARGET)

$(TARGET): $(SRCS)
	$(CC) $(CFLAGS) $(SRCS) -o $(TARGET)
install: all
	install -m 755 $(TARGET) $(PREFIX)/bin/
	install -m 644 $(TARGET).service /etc/systemd/system/
	systemctl daemon-reload
uninstall:
	systemctl stop $(TARGET) || true
	systemctl disable $(TARGET) || true
	rm -f $(PREFIX)/bin/$(TARGET)
	rm -f /etc/systemd/system/$(TARGET).service
	systemctl daemon-reload

clean:
	rm -f $(TARGET)
