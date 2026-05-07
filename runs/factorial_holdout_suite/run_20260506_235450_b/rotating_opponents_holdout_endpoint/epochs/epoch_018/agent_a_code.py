def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for a in (observation.get("obstacles") or []):
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obs.add((int(a[0]), int(a[1])))
        elif isinstance(a, dict) and "x" in a and "y" in a:
            obs.add((int(a["x"]), int(a["y"])))

    def parse_xy(r):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return int(r[0]), int(r[1])
        if isinstance(r, dict) and "x" in r and "y" in r:
            return int(r["x"]), int(r["y"])
        return None

    resources = []
    for r in (observation.get("resources") or []):
        p = parse_xy(r)
        if p is not None:
            resources.append(p)

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        lead = od - sd  # positive means we are closer
        # Prefer guaranteed lead; tie-break deterministically by coordinate
        key = (-lead, sd, rx, ry) if lead > 0 else (0, sd - od, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best if best is not None else resources[0]
    cur_d = man(sx, sy, tx, ty)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            # Prefer smaller distance, then also avoid moving into opponent vicinity slightly
            opp_pen = man(nx, ny, ox, oy)
            moves.append((d, -opp_pen, dx, dy))

    if not moves:
        return [0, 0]
    moves.sort()
    dx, dy = moves[0][2], moves[0][3]
    if man(sx + dx, sy + dy, tx, ty) > cur_d:
        # fallback: stay if we didn't improve
        return [0, 0]
    return [int(dx), int(dy)]