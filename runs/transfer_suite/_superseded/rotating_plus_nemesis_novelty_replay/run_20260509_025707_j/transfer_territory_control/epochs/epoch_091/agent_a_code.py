def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation.get("opponent_position", (sx, sy))
    obs = observation.get("obstacles") or []
    obstacles = set(tuple(p) for p in obs)
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def man(x, y):
        return abs(x - ox) + abs(y - oy)
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d = man(nx, ny)
        near = (abs(nx - ox) <= 1 and abs(ny - oy) <= 1) and not (nx == ox and ny == oy)
        score = -d + (5 if near else 0)
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]
    if best is not None:
        return best
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            return [dx, dy]
    return [0, 0]