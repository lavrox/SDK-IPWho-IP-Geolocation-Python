"""Live smoke test. Set IPWHO_API_KEY and run: python3 test_ipwho.py"""

import os
import sys

from ipwho import IPWhoClient, IPWhoError

p = f = 0


def ok(c, msg):
    global p, f
    if c:
        p += 1
        print("  PASS", msg)
    else:
        f += 1
        print("  FAIL", msg)


def main():
    api_key = os.environ.get("IPWHO_API_KEY", "")
    if not api_key:
        print("Set IPWHO_API_KEY to run the live smoke test.")
        sys.exit(0)

    c = IPWhoClient(api_key)

    r = c.lookup("8.8.8.8")
    d = r.data
    gl, tz, fl, cu, cn = d.geo_location, d.timezone, d.flag, d.currency, d.connection
    ok(d.ip == "8.8.8.8", "lookup ip == 8.8.8.8")
    ok(gl.country == "United States", f"country == United States (got {gl.country})")
    ok(cn.asn_number == 15169, f"asn_number == 15169 (got {cn.asn_number})")
    ok(gl.dial_code is not None, f"dial_code captured ({gl.dial_code})")
    ok(gl.is_in_eu is not None, "is_in_eu captured")
    ok(tz.time_zone is not None, f"time_zone captured ({tz.time_zone})")
    ok(fl.flag_icon is not None, f"flag_Icon captured ({fl.flag_icon})")
    ok(fl.flag_unicode is not None, f"flag_unicode captured ({fl.flag_unicode})")
    ok(cu.name_plural is not None, f"name_plural captured ({cu.name_plural})")
    ok(cn.asn_org is not None, f"asn_org captured ({cn.asn_org})")
    ok(cn.connection_type is not None, f"connection_type captured ({cn.connection_type})")

    me = c.me()
    ok(me.data.ip not in (None, ""), f"me ip captured ({me.data.ip})")

    b = c.bulk(["8.8.8.8", "1.1.1.1"])
    ra = b.data.response_array
    ok(ra is not None and len(ra) == 2, f"bulk returns 2 (got {len(ra) if ra else 'None'})")

    try:
        IPWhoClient("sk.invalid_test_key").lookup("8.8.8.8")
        ok(False, "bad key should raise")
    except IPWhoError as e:
        ok(True, f"bad key raised {type(e).__name__}")
    except Exception as e:
        ok(True, f"bad key raised {type(e).__name__}")

    print(f"\nPYTHON RESULT: {p} passed, {f} failed")
    sys.exit(1 if f else 0)


if __name__ == "__main__":
    main()
