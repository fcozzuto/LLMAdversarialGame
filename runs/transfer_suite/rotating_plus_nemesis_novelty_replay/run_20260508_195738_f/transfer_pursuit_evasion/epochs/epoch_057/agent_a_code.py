def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    is_evader = ("evad" in self_role) or (("agent" in self_role) and ("evad" in opp_role))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Determine desired heading: pursuer moves toward opponent; evader moves away.
    vx = ox - sx
    vy = oy - sy
    if is_evader:
        vx, vy = -vx, -vy

    step_x = 0 if vx == 0 else (1 if vx > 0 else -1)
    step_y = 0 if vy == 0 else (1 if vy > 0 else -1)

    # Tie-breaker preference: slight wall-following by preferring safer directions when blocked.
    def score_move(nx, ny):
        if (nx, ny) in obs:
            return -10**9
        d = dist2(nx, ny, ox, oy)
        # For pursuer: maximize reduction (min d). For evader: maximize distance (max d).
        primary = -d if not is_evader else d

        # Obstacle proximity penalty
        prox = 0
        for ax in range(-1, 2):
            for ay in range(-1, 2):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obs:
                    prox += 1
        penalty = prox * 8

        # Edge/compass preference to keep motion decisive (avoids dithering)
        edge_pen = 0
        if nx == 0 or nx == w - 1:
            edge_pen += 2
        if ny == 0 or ny == h - 1:
            edge_pen += 2

        # Encourage matching the desired step direction (except when forced around obstacles)
        align = -0.5 if (nx - sx) != step_x else 0.5
        align += -0.5 if (ny - sy) != step_y else 0.5

        return primary - penalty - edge_pen + align

    best = (0, 0)
    best_sc = -10**18
    # Evaluate directions in a deterministic order biased toward desired step.
    ordered = []
    for dx, dy in dirs:
        if (dx, dy) == (step_x, step_y):
            ordered.append((dx, dy))
    for dx, dy in dirs:
        if (dx, dy) != (step_x, step_y):
            ordered.append((dx, dy))

    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = score_move(nx, ny)
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]