def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def mhd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Choose a target we can reach sooner than the opponent; also contest on opponent's current row/col.
    best = resources[0]
    best_val = -10**18
    for rx, ry in resources:
        self_d = mhd(sx, sy, rx, ry)
        opp_d = mhd(ox, oy, rx, ry)
        value = (opp_d - self_d) * 10 - self_d
        if ry == oy: value += 6
        if rx == ox: value += 3
        if ry == sy: value += 1
        if rx == sx: value += 1
        if value > best_val:
            best_val = value
            best = (rx, ry)

    tx, ty = best
    # Move toward target; avoid stepping into obstacles when possible.
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            if mx == 0 and my == 0:
                candidates.append((mx, my, 0))
                continue
            nx, ny = sx + mx, sy + my
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                # Prefer moves that reduce distance to target; break ties with contest effect.
                d_to = mhd(nx, ny, tx, ty)
                d_opp = mhd(ox, oy, tx, ty)
                bias = (d_opp - d_to) * 2 - d_to
                # Also favor aligning movement with dx/dy direction.
                align = 0
                if mx == dx: align += 1
                if my == dy: align += 1
                candidates.append((mx, my, bias + align))

    # Deterministic selection: max score, then fixed order.
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-t[2], t[0], t[1]))
    return [int(candidates[0][0]), int(candidates[0][1])]