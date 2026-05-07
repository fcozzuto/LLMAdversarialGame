def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    if not res:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny) and not (nx == ox and ny == oy):
                return [dx, dy]
        return [0, 0]

    if (sx, sy) in obst:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    def score_to_target(tx, ty, nx, ny):
        return abs(tx - nx) + abs(ty - ny)

    best = None
    best_score = None
    for dx, dy in moves[1:]:  # prefer moving over staying
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        s = min(score_to_target(rx, ry, nx, ny) for rx, ry in res)
        # small tie-break toward reducing distance from opponent to reduce being chased
        s = (s, abs(ox - nx) + abs(oy - ny))
        if best_score is None or s < best_score:
            best_score = s
            best = (dx, dy)

    if best is not None:
        return [best[0], best[1]]

    # fallback: staying (only if valid)
    if valid(sx, sy):
        return [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
    return [0, 0]