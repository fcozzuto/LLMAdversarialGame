def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    target = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        # Prefer resources we can arrive sooner, then closer to us.
        key = (od - sd, -sd, -manh(ox, oy, rx, ry))
        if best_key is None or key > best_key:
            best_key = key
            target = (rx, ry)

    if target is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = target

    deltas = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            deltas.append((dx, dy))

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        self_d = manh(nx, ny, tx, ty)
        opp_d = manh(nx, ny, ox, oy)
        cur_d = manh(sx, sy, tx, ty)
        progress = cur_d - self_d
        # Tie-break deterministically by preferring diagonal/forward implicitly via ordered deltas.
        score = (-self_d, progress, opp_d)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]