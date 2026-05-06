def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]
    obs_set = set((p[0], p[1]) for p in obstacles)
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dsq(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy
    deltas = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = deltas[0]
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            v = -dsq(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best
    best = deltas[0]
    bestv = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        v = -10**18
        for rx, ry in resources:
            d1 = dsq(nx, ny, rx, ry)
            d2 = dsq(ox, oy, rx, ry)
            cand = -d1 + 0.6 * (d2 - d1)  # prefer being closer than opponent
            if cand > v:
                v = cand
        # small tie-break to get closer to nearest resource
        if v == -10**18:
            v = -dsq(nx, ny, resources[0][0], resources[0][1])
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best