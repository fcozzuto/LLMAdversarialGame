def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Prefer resources where we can arrive no later (or much earlier).
    best = None
    best_key = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        ahead = od - sd
        # Key: maximize ahead; then prefer shorter self distance; then deterministic by coords.
        key = (ahead, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                nx, ny = sx, sy
                dx, dy = 0, 0
            moves.append((dx, dy, nx, ny))

    # Score next positions: get closer to target; if tied, ensure not giving opponent an easier access.
    best_move = [0, 0]
    best_score = None
    for dx, dy, nx, ny in moves:
        self_d = md(nx, ny, tx, ty)
        opp_d = md(ox, oy, tx, ty)
        score = (opp_d - self_d, -self_d, -abs(nx - ox) - abs(ny - oy), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move