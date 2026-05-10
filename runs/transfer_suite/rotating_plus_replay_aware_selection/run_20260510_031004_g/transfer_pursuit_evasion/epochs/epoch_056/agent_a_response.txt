def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except Exception:
            pass

    self_role = (observation.get("self_role", "") or "").lower()
    opponent_role = (observation.get("opponent_role", "") or "").lower()
    if "evad" in self_role:
        is_pursuer = False
    elif "evad" in opponent_role:
        is_pursuer = True
    else:
        is_pursuer = True

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_pursuer:
        tx, ty = ox, oy
    else:
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = None

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        d_opp = dist(nx, ny, ox, oy)
        d_tgt = dist(nx, ny, tx, ty)

        if is_pursuer:
            # primary: get closer to opponent; secondary: keep moving toward target
            val = -d_opp * 10 - d_tgt
        else:
            # primary: get farther from opponent; secondary: move toward best corner
            val = d_opp * 10 - d_tgt

        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]