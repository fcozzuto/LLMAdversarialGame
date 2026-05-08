def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    unclaimed = [(p[0], p[1]) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2]
    opp_terr = [(p[0], p[1]) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    candidates = unclaimed if unclaimed else opp_terr
    if not candidates:
        return [0, 0]

    # Prefer center denial: near center, and we are at least as close as opponent (or better).
    best = None
    best_score = None
    for (x, y) in candidates:
        d1 = md(sx, sy, x, y)
        d2 = md(ox, oy, x, y)
        dc = abs(x - cx) + abs(y - cy)
        # Higher priority when we can arrive earlier; otherwise still contest center.
        score = (dc, d1 - d2, d1, y, x)
        if best_score is None or score < best_score:
            best_score = score
            best = (x, y)

    tx, ty = best
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = [0, 0]
    best_k = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        k = (md(nx, ny, tx, ty), abs(nx - cx) + abs(ny - cy), nx, ny)
        if best_k is None or k < best_k:
            best_k = k
            best_m = [dx, dy]
    return best_m