def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in self_role) or ("runner" in self_role) or ("escape" in self_role)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Direction preference: pursuer goes toward opponent, evader goes away.
    tx = ox - sx
    ty = oy - sy
    if tx == 0 and ty == 0:
        sgnx = sgny = 0
    else:
        sgnx = 0 if tx == 0 else (1 if tx > 0 else -1)
        sgny = 0 if ty == 0 else (1 if ty > 0 else -1)

    desired = (sgnx, sgny)
    best = None
    best_val = None

    # Wall-run / obstacle awareness: evaluate local moves by resulting distance and obstacle avoidance.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Base objective: maximize progress for pursuer, maximize survival distance for evader.
        d2 = dist2(nx, ny, ox, oy)
        if is_evader:
            val = d2
            # Extra: avoid being boxed in near obstacles by penalizing many blocked neighbors.
            blocked = 0
            for adx, ady in moves:
                ax, ay = nx + adx, ny + ady
                if not ok(ax, ay):
                    blocked += 1
            val -= 0.35 * blocked
            # Extra: avoid edges when evading (deterministic corner avoidance).
            edge_pen = (nx == 0) + (ny == 0) + (nx == w - 1) + (ny == h - 1)
            val -= 0.25 * edge_pen
        else:
            val = -d2
            # Extra: discourage moves that increase obstacle blockage around us.
            blocked = 0
            for adx, ady in moves:
                ax, ay = nx + adx, ny + ady
                if not ok(ax, ay):
                    blocked += 1
            val -= 0.15 * blocked
            # Extra: prefer moves aligned with desired direction to reduce oscillation.
            align = (dx == desired[0]) + (dy == desired[1])
            val += 0.05 * align
            # Extra: if desired diagonal step is blocked, keep moving around the obstacle deterministically.
            if dx == desired[0] and dy == desired[1]:
                val += 0.02

        if best is None or val > best_val:
            best = [dx, dy]
            best_val = val

    # Fallback (shouldn't happen): try any in-bounds non-obstacle move deterministically.
    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    return best