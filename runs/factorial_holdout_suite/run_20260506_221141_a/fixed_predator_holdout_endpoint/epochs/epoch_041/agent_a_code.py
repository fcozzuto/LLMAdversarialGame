def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    if not res:
        return [0, 0]

    turns = int(observation.get("turns_remaining", 0) or 0)

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_key = None
    for rx, ry in res:
        myd = manh(sx, sy, rx, ry)
        opd = manh(ox, oy, rx, ry)
        time_bias = 0 if turns <= 0 else (turns - myd)
        # Prefer taking resources opponent can't reach first; also prefer earlier/closer.
        adv = (opd - myd) * 2 + (time_bias > 0) * 1 - myd * 0.1
        key = (adv, -myd)  # maximize adv, then minimize myd
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # Candidate moves in deterministic priority (diagonal first when both help, then single-axis).
    dx1 = 0 if tx == sx else (1 if tx > sx else -1)
    dy1 = 0 if ty == sy else (1 if ty > sy else -1)
    cand = []
    cand.append((dx1, dy1))
    cand.append((dx1, 0))
    cand.append((0, dy1))
    cand.append((0, 0))

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            return [int(dx), int(dy)]

    return [0, 0]