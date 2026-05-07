def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, dict) and "x" in a and "y" in a:
            obs.add((int(a["x"]), int(a["y"])))
        elif isinstance(a, (list, tuple)) and len(a) >= 2:
            obs.add((int(a[0]), int(a[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, dict) and "x" in r and "y" in r:
            x, y = int(r["x"]), int(r["y"])
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    best = None
    best_t = None
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        parity = ((rx + ry) & 1)
        adv = opd - myd  # positive means we are closer
        # Prefer decisive advantages; then closer; then deterministic parity
        score = adv * 1000 - myd * 5 + parity
        if best is None or score > best:
            best = score
            best_t = (rx, ry)

    tx, ty = best_t

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obs:
                continue
            myd_next = dist(nx, ny, tx, ty)
            # If we can't win that resource, still reduce distance; add slight preference to be farther from opponent
            risk = dist(nx, ny, ox, oy)
            moves.append((myd_next, -risk, dx, dy))
    moves.sort()
    if not moves:
        return [0, 0]
    return [int(moves[0][2]), int(moves[0][3])]