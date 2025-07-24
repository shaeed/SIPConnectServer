#!/bin/sh
echo "Available /dev/tty* devices:"
ls -l /dev/ttyUSB*

echo ""
echo "Checking if they are accessible:"
for dev in /dev/ttyUSB*; do
  echo "Trying $dev..."
  if [ -r "$dev" ] && [ -w "$dev" ]; then
    echo "  ✅ $dev is readable & writable"
  else
    echo "  ⚠️  $dev is NOT fully accessible"
  fi
done
