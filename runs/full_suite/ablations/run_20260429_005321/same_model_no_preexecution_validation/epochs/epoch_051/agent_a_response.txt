def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obstacles)

    if not resources:
        return [0, 0]
    if (sx, sy) in set((r[0], r[1]) for r in resources):
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return dx if dx >= 0 else -dx if dy == 0 else (dy if dy >= 0 else -dy)  # overwritten below

    def dist(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        md = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # maximize advantage (opponent farther than us). If equal, prefer closer.
        key = (od - md, -md, -(rx + ry), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        md2 = dist(nx, ny, tx, ty)
        od2 = dist(ox, oy, tx, ty)
        # primary: get closer to target; secondary: don't worsen (proxy); tertiary deterministic order
        key = (-md2, -od2, dx != 0 and dy != 0, -abs(dx) - abs(dy), dx, dy)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]