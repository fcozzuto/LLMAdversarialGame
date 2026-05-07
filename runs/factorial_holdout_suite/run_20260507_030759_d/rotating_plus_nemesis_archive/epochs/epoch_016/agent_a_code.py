def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    res = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass
    resources = []
    for p in res:
        try:
            resources.append((int(p[0]), int(p[1])))
        except Exception:
            pass

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    # Pick a target resource where we are relatively closer than opponent.
    best = None
    best_key = None
    for tx, ty in resources:
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        key = (do - ds, -ds, -do, tx, ty)
        if best is None or key > best_key:
            best = (tx, ty)
            best_key = key
    tx, ty = best

    # Choose move maximizing (opp_dist - self_dist) after the move.
    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Assume opponent does not move for scoring; still improves reach advantage.
        ds2 = md(nx, ny, tx, ty)
        do2 = md(ox, oy, tx, ty)
        val = (do2 - ds2, -ds2, dx, dy)
        if best_move is None or val > best_val:
            best_move = (dx, dy)
            best_val = val

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]