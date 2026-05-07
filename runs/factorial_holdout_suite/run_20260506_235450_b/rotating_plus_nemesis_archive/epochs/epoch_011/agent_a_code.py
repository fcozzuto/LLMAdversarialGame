def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list if p is not None and len(p) >= 2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    tx, ty = (w - 1) // 2, (h - 1) // 2
    best = [0, 0]
    bestv = -10**18

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            myd = min(dist(nx, ny, r[0], r[1]) for r in resources)
            opd = min(dist(ox, oy, r[0], r[1]) for r in resources)
            v = (opd - myd) * 1000 - dist(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # No visible resources: move toward center while staying away from opponent if possible
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = -dist(nx, ny, tx, ty) - max(0, 3 - dist(nx, ny, ox, oy)) * 10
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best