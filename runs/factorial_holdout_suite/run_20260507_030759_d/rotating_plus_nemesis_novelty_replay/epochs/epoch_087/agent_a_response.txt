def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds  # positive if we arrive earlier
        # Tie-break: prefer closer lead, also prefer resources more "ours" by distance difference.
        # Small center bias to reduce dithering.
        cx = (w - 1) * 0.5
        cy = (h - 1) * 0.5
        center_bias = -((rx - cx) * (rx - cx) + (ry - cy) * (ry - cy)) * 0.01
        key = (lead, -ds, center_bias)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0
    dy = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    if ty > sy: dy = 1
    elif ty < sy: dy = -1

    # If intended cell is blocked, try deterministic local alternatives.
    cand = []
    cand.append((dx, dy))
    if dx != 0: cand.append((dx, 0))
    if dy != 0: cand.append((0, dy))
    cand.append((0, 0))
    if dx != 0 and dy != 0:
        cand.append((dx, -dy))
        cand.append((-dx, dy))

    # Deterministic choice order: first valid, else stay.
    for mx, my in cand:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(mx), int(my)]
    return [0, 0]