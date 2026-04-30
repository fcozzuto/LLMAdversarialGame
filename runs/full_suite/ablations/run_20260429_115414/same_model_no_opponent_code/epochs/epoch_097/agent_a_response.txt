def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def in_bounds(x, y): return 0 <= x < w and 0 <= y < h
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def sgn(v): return (v > 0) - (v < 0)

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if in_bounds(rx, ry) and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Target selection: first pick a resource we can reach no later than opponent (prefer closer),
    # otherwise pick a resource maximizing (opp_dist - self_dist), with deterministic tie-break.
    best = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        if od >= sd:
            key = (0, sd, -rx, -ry)  # reach-or-beat opponent; closer first
        else:
            key = (1, -(od - sd), -sd, -rx, -ry)  # maximize advantage (opp slower); then prefer smaller sd
        if best is None or key < best[0]:
            best = (key, (rx, ry), sd, od)

    tx, ty = (sx, sy) if best is None else best[1]

    # Move selection: avoid obstacles, prefer moves that reduce distance to target and avoid giving opponent progress.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        self_to_t = md(nx, ny, tx, ty)
        opp_to_t = md(ox, oy, tx, ty)
        sd_now = md(sx, sy, tx, ty)
        # Opponent "pressure" estimate: how much closer opponent is to target than we'd be after the move.
        after_pressure = opp_to_t - self_to_t
        # Obstacle/edge gentle penalty via staying near bounds already handled by bounds.
        # Deterministic tie-break by dx,dy ordering.
        score = (self_to_t, after_pressure, md(nx, ny, ox, oy), sd_now - self_to_t, -dx, -dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]