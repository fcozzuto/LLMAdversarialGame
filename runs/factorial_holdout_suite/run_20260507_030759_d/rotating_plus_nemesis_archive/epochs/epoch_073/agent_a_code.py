def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    try:
        w = int(w)
        h = int(h)
    except:
        w, h = 8, 8
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = sp[0], sp[1]
    ox, oy = op[0], op[1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    def dist(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        dS = dist(sx, sy, rx, ry)
        dO = dist(ox, oy, rx, ry)
        # Prefer resources we can reach sooner; otherwise try to deny opponent.
        key = (dS - dO, dS, -(ry == oy), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    dx = 0
    dy = 0
    if rx > sx: dx = 1
    elif rx < sx: dx = -1
    if ry > sy: dy = 1
    elif ry < sy: dy = -1

    # Prefer axis move that brings us closer; avoid obstacles when possible.
    cand = []
    if dx != 0:
        cand.append((dx, 0))
        cand.append((dx, dy))
    if dy != 0:
        cand.append((0, dy))
        cand.append((dx, dy))
    cand.append((0, 0))

    seen = set()
    for mx, my in cand:
        if (mx, my) in seen:
            continue
        seen.add((mx, my))
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            # Deterministic closer check to target
            before = dist(sx, sy, rx, ry)
            after = dist(nx, ny, rx, ry)
            if after <= before:
                return [int(mx), int(my)]

    return [0, 0]