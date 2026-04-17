def ra_to_deg(h, m, s):
    return (h + m / 60.0 + s / 3600.0) * 15.0


def dec_to_deg(d, m, s, sign=1):
    return sign * (abs(d) + m / 60.0 + s / 3600.0)


# SN 1991bg: 12:25:04.07, +12:53:13.1
print(f"1991bg: RA {ra_to_deg(12, 25, 4.07):.6f}, Dec {dec_to_deg(12, 53, 13.1):.6f}")

# SN 1991T: 12:43:15.15, +02:38:15.4
print(f"1991T: RA {ra_to_deg(12, 43, 15.15):.6f}, Dec {dec_to_deg(2, 38, 15.4):.6f}")

# SN 1994D: 12:34:02.45, +07:42:04.7
print(f"1994D: RA {ra_to_deg(12, 34, 2.45):.6f}, Dec {dec_to_deg(7, 42, 4.7):.6f}")

# SN 1999by: 13:20:10.55, +34:24:59.8
print(f"1999by: RA {ra_to_deg(13, 20, 10.55):.6f}, Dec {dec_to_deg(34, 24, 59.8):.6f}")

# SN 2002bo: 10:18:06.51, +21:49:41.9
print(f"2002bo: RA {ra_to_deg(10, 18, 6.51):.6f}, Dec {dec_to_deg(21, 49, 41.9):.6f}")

# SN 2005cf: 15:21:32.21, -07:24:46.9
ra_cf = ra_to_deg(15, 21, 32.21)
dec_cf = dec_to_deg(7, 24, 46.9, sign=-1)
print(f"2005cf: RA {ra_cf:.6f}, Dec {dec_cf:.6f}")


# SN 2009ig: 23:15:35.55, +09:14:34.5
print(f"2009ig: RA {ra_to_deg(23, 15, 35.55):.6f}, Dec {dec_to_deg(9, 14, 34.5):.6f}")

# SN 2014J: 09:55:42.12, +69:40:25.9
print(f"2014J: RA {ra_to_deg(9, 55, 42.12):.6f}, Dec {dec_to_deg(69, 40, 25.9):.6f}")
