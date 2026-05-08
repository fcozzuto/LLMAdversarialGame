def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if p is not None:
            obst.add((p[0], p[1]))
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not resources:
        return [0, 0]

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        rmin = None
        for rx, ry in resources:
            d = max(abs(nx - rx), abs(ny - ry))
            if rmin is None or d < rmin:
                rmin = d
        od = max(abs(nx - ox), abs(ny - oy))
        score = (-rmin if rmin is not None else 0) + (0.2 * od) - (0.05 * (dx == 0 and dy == 0))
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]