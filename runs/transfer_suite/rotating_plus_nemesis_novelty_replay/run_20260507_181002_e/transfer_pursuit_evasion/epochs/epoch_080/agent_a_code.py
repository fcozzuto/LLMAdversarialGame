def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role", "")) or ""
    is_evader = ("evad" in role.lower())

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_block(x, y):
        c = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                if (x + ex, y + ey) in obstacles:
                    c += 1
        return c

    def boundary_pen(x, y):
        # prefer staying away from walls unless blocked by obstacles
        d = min(x, y, w - 1 - x, h - 1 - y)
        return -0.15 * (d == 0) - 0.06 * (d == 1)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)

        # Chase or flee, plus obstacle and wall avoidance.
        if is_evader:
            base = dist2
        else:
            base = -dist2

        # Nudge to move roughly toward/away in dominant axis to reduce zigzag.
        ddx = 0 if ox == nx else (1 if ox > nx else -1)
        ddy = 0 if oy == ny else (1 if oy > ny else -1)
        axis_nudge = (ddx * dx + ddy * dy)
        if is_evader:
            axis_nudge = -axis_nudge

        # If role changes, still robust due to obstacle penalties.
        score = base + 0.25 * axis_nudge - 0.12 * adj_block(nx, ny) + boundary_pen(nx, ny)

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]