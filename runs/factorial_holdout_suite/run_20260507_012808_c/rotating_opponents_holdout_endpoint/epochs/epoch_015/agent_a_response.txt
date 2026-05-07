def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is None or len(r) < 2:
            continue
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_score = None
    for tx, ty in resources:
        sd = md(sx, sy, tx, ty)
        od = md(ox, oy, tx, ty)
        # Prefer resources we can win (sd < od), also avoid long detours.
        # Tie-break: prefer smaller sd, then closer to center, then lexicographic.
        center_bias = (abs(tx - cx) + abs(ty - cy)) * 1e-3
        score = (sd - od, sd, center_bias, tx, ty)
        if best is None or score < best_score:
            best, best_score = (tx, ty), score

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If diagonal would be "worse" by letting opponent grab immediately, try orthogonal step.
    if dx != 0 and dy != 0:
        d_diag = md(sx + dx, sy + dy, tx, ty)
        # Opponent next-step distance to target approximated by minimal Chebyshev toward target.
        adx = 0 if tx == ox else (1 if tx > ox else -1)
        ady = 0 if ty == oy else (1 if ty > oy else -1)
        od_diag = md(ox + adx, oy + ady, tx, ty)
        if d_diag - od_diag > md(sx + dx, sy, tx, ty) - od_diag:
            dy = 0
        elif d_diag - od_diag > md(sx, sy + dy, tx, ty) - od_diag:
            dx = 0

    return [int(dx), int(dy)]