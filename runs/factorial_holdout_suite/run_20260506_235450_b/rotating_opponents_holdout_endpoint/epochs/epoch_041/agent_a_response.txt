def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, dict) and "x" in a and "y" in a:
            x, y = int(a["x"]), int(a["y"])
        elif isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def parse_xy(v):
        if isinstance(v, dict) and "x" in v and "y" in v:
            return int(v["x"]), int(v["y"])
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return None

    resources = []
    for r in observation.get("resources") or []:
        p = parse_xy(r)
        if not p:
            continue
        x, y = p
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    # Pick target that is better relative to opponent: larger (opp_dist - self_dist).
    best = None
    for x, y in resources:
        sd = man(sx, sy, x, y)
        od = man(ox, oy, x, y)
        key = (od - sd, -sd, -x, -y)
        if best is None or key > best[0]:
            best = (key, (x, y))
    tx, ty = best[1]

    def score_move(nx, ny):
        sd = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)
        # Also prefer moves that reduce direct distance to target.
        # Tie-break: keep within bounds and avoid obstacles strongly.
        pen_obs = 100000 if (nx, ny) in obstacles else 0
        # Nudge toward clearing in 2D (diagonal-capable).
        dx1 = nx - sx
        dy1 = ny - sy
        diag = 1 if dx1 != 0 and dy1 != 0 else 0
        return pen_obs + 10 * sd + od - diag

    best_move = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            val = score_move(nx, ny)
            if best_move is None or val < best_move[0] or (val == best_move[0] and (dx, dy) < best_move[1]):
                best_move = (val, (dx, dy))
    return [best_move[1][0], best_move[1][1]]