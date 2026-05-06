def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    cx, cy = w // 2, h // 2

    # Choose a guarded target: prefer resources where we are not worse than opponent.
    best = (cx, cy)
    best_score = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = r[0], r[1]
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        # "Guarded advantage": strong preference to be clearly closer; otherwise avoid/ignore.
        val = sd
        if od < sd:
            val += 6 + (sd - od)  # heavily penalize contested/losing positions
        # Mild tie-break: prefer nearer to center to reduce future contest.
        val += 0.1 * man(tx, ty, cx, cy)
        if best_score is None or val < best_score or (val == best_score and (tx, ty) < best):
            best_score = val
            best = (tx, ty)

    tx, ty = best

    # One-step lookahead with obstacle handling and opponent avoidance.
    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    best_move = (0, 0)
    best_h = None
    for dx, dy, nx, ny in cand:
        myd = man(nx, ny, tx, ty)
        old_my_d = man(sx, sy, tx, ty)
        od = man(nx, ny, ox, oy)

        # Keep moving meaningfully toward target; avoid stepping into opponent vicinity.
        # Also prefer non-worsening progress.
        prog = myd - old_my_d
        opp_pen = 0 if od >= 3 else (6 - od) * 1.5
        center_bias = 0.05 * man(nx, ny, cx, cy)

        h = prog + opp_pen + center_bias + 0.02 * myd
        if best_h is None or h < best_h or (h == best_h and (dx, dy) < best_move):
            best_h = h
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]