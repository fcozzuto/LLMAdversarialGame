def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    opp = tuple(observation.get("opponent_position") or (sx, sy))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = -10**18
    ox, oy = opp

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        val = 0
        if (nx, ny) in unclaimed:
            val += 100000
        ddx, ddy = nx - ox, ny - oy
        val -= ddx * ddx + ddy * ddy
        if best is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is not None:
        return best
    if legal(sx, sy):
        return [0, 0]
    for dx, dy in moves:
        if legal(sx + dx, sy + dy):
            return [dx, dy]
    return [0, 0]