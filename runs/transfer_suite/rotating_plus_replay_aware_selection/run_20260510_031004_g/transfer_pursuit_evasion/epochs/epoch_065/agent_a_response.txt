def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = None
    if "purs" in self_role:
        is_pursuer = True
    elif "evad" in self_role:
        is_pursuer = False
    if is_pursuer is None:
        if "evad" in opp_role:
            is_pursuer = False
        elif "purs" in opp_role:
            is_pursuer = True
    if is_pursuer is None:
        is_pursuer = True

    obs = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except Exception:
            pass

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h:
                if (nx, ny) not in obs:
                    moves.append((dx, dy))
    if not moves:
        moves = [(0, 0)]

    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Greedy with deterministic tie-break; add a mild "obstacle pressure" term.
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        base = d2(nx, ny, ox, oy)
        # penalty if adjacent to obstacle (to avoid getting trapped)
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obs:
                    adj_pen += 1
        # small deterministic bias toward moving diagonally to reach corners faster
        diag_bias = 0.001 * (dx != 0 and dy != 0)
        score = (base + 0.15 * adj_pen + diag_bias) if is_pursuer else -(base - 0.15 * adj_pen - diag_bias)
        if best is None or (score < best_score if is_pursuer else score > best_score):
            best = (dx, dy)
            best_score = score
        elif score == best_score:
            # tie-break: prefer smallest dx then dy deterministically (stable)
            if (dx, dy) < best:
                best = (dx, dy)

    if best is None:
        best = (0, 0)
    return [int(best[0]), int(best[1])]