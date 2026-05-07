def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_score(px, py):
        best = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            tx, ty = int(r[0]), int(r[1])
            if (tx, ty) in obst:
                continue
            self_d = md(px, py, tx, ty)
            opp_d = md(ox, oy, tx, ty)
            key = (opp_d - self_d, -self_d, -tx, -ty)
            if best is None or key > best:
                best = key
        return best

    # Evaluate immediate best move deterministically
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Prefer staying only if no moves are safe/better.
    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        score_key = best_score(nx, ny)
        if score_key is None:
            key = (0, 0, 0, 0)
        else:
            # small tie-break to prefer progressing (avoid dithering)
            key = (score_key[0], score_key[1], -abs(dx) - abs(dy), -(nx + ny))
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    # If all candidate moves were blocked, stay.
    return [int(best_move[0]), int(best_move[1])]