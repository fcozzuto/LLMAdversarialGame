def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("hunt" in role) or ("chaser" in role) or ("seeker" in role) or ("hunter" in role)

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y, tx, ty):
        dx, dy = x - tx, y - ty
        return dx * dx + dy * dy

    def obs_pen(x, y):
        pen = 0
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) in obstacles:
                pen += 1
        return pen

    def clamp_dir(a, b):
        if b > a:
            return 1
        if b < a:
            return -1
        return 0

    # If very cornered/obstacle-heavy, bias along the most direct axis to avoid stalling.
    bias_dx = clamp_dir(sx, ox)
    bias_dy = clamp_dir(sy, oy)

    best = None
    best_val = None
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        ppen = obs_pen(nx, ny)
        axis_b = 0 if (dx == bias_dx and dy == bias_dy) else 1
        if is_pursuer:
            val = d + 2.0 * ppen + 0.25 * axis_b
            better = best_val is None or val < best_val
        else:
            # Evader: maximize distance while staying away from obstacles.
            val = d - 2.0 * ppen - 0.25 * axis_b
            better = best_val is None or val > best_val
        if better:
            best_val = val
            best = (dx, dy)

    if best is None:
        # Fallback to deterministic safe move (prefer stay, then N/S/E/W toward opponent for pursuer; away for evader).
        dx = clamp_dir(sx, ox)
        dy = clamp_dir(sy, oy)
        cand = [(0, 0), (dx, 0), (0, dy), (dx, dy), (-dx, 0), (0, -dy)]
        for ddx, ddy in cand:
            nx, ny = sx + ddx, sy + ddy
            if ok(nx, ny):
                return [int(ddx), int(ddy)]
        return [0, 0]

    return [int(best[0]), int(best[1])]