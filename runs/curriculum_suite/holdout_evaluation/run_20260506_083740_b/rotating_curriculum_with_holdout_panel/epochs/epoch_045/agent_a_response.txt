def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    res = []
    for r in resources:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                res.append((rx, ry))
    if not res:
        return [0, 0]

    # New policy: maximize immediate "advantage" on the best resource we could contest next.
    # If we're losing overall, this naturally steers toward resources where we can flip to ahead.
    best = (None, -10**9, None)  # (move, score, tie_d)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        best_score = -10**9
        best_dme = 10**9
        for rx, ry in res:
            dme = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            # Score: how much closer we are than opponent to the same resource.
            # Add small preference for smaller absolute distance and for being closer on diagonal moves too.
            s = (do - dme) * 10 - dme
            if s > best_score or (s == best_score and dme < best_dme):
                best_score = s
                best_dme = dme
        # Extra small penalty if move increases our distance to the currently best target (discourage dithering).
        # Deterministic: use best_dme only.
        if best[0] is None or best_score > best[1] or (best_score == best[1] and best_dme < best[2]):
            best = ((dx, dy), best_score, best_dme)

    return [int(best[0][0]), int(best[0][1])]