def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    ap = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    blocked = set()
    for ob in observation.get("obstacles") or []:
        x = y = None
        if isinstance(ob, (list, tuple)) and len(ob) >= 2:
            x, y = int(ob[0]), int(ob[1])
        elif isinstance(ob, dict):
            if "x" in ob and "y" in ob:
                x, y = int(ob["x"]), int(ob["y"])
            else:
                p = ob.get("position")
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    x, y = int(p[0]), int(p[1])
        if x is not None and y is not None and 0 <= x < w and 0 <= y < h:
            blocked.add((x, y))

    resources = observation.get("resources") or []
    rlist = []
    for r in resources:
        x = y = None
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        elif isinstance(r, dict):
            if "x" in r and "y" in r:
                x, y = int(r["x"]), int(r["y"])
            else:
                p = r.get("position")
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    x, y = int(p[0]), int(p[1])
        if x is not None and y is not None and 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
            rlist.append((x, y))
    if not rlist:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    mypos = (sx, sy)
    opp = (ox, oy)

    best = None
    best_key = None
    for rx, ry in rlist:
        myd = man(mypos, (rx, ry))
        opd = man(opp, (rx, ry))
        # Prefer resources we can reach earlier; otherwise still prefer the "most deniable" ones.
        # Key: higher denial gap, then shorter my distance, then deterministic tie by coordinates.
        key = (opd - myd, -myd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        newpos = (nx, ny)
        myd2 = man(newpos, (tx, ty))
        opd2 = man(opp, (tx, ty))
        # Keep moving toward target while maintaining lead and avoiding stepping away.
        mkey = (opd2 - myd2, -myd2, -nx, -ny, -abs(dx) - abs(dy))
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]