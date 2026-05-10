def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = True
    if "evad" in self_role:
        is_pursuer = False
    elif "evad" in opp_role:
        is_pursuer = True

    obs = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except Exception:
            pass

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corner_targets = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corner_targets, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    near_corner = min(corner_targets, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        d = md(nx, ny, ox, oy)
        if is_pursuer:
            target_corner = far_corner
            corner_d = md(nx, ny, target_corner[0], target_corner[1])
            # Prefer reducing distance to opponent; also stay heading to far corner.
            val = (-d * 1000) + (-corner_d)
        else:
            target_corner = near_corner
            corner_d = md(nx, ny, target_corner[0], target_corner[1])
            # Prefer increasing distance from pursuer; also move toward near corner (to be harder to trap).
            val = (d * 1000) + (-corner_d)

        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    return best if best is not None else [0, 0]