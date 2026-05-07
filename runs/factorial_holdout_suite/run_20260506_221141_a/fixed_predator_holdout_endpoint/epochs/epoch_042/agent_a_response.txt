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
        # Primary: can we arrive earlier; Secondary: arrive soon; Tertiary: break ties deterministically.
        win = opd - myd
        time_focus = 0 if turns <= 0 else (turns - myd)
        key = (win, time_focus, -myd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_to_target = manh(nx, ny, tx, ty)
        # Discourage stepping into opponent-faster cells slightly
        d_to_opp = manh(nx, ny, ox, oy)
        score = (-d_to_target, -(d_to_opp - d_to_target), -abs(d_to_target - manh(sx, sy, tx, ty)))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move