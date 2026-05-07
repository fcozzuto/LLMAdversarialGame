def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    def legal(x, y): return inb(x, y) and (x, y) not in obstacles

    if not resources:
        tx = 7 if sx < gw // 2 else 0
        ty = 7 if sy < gh // 2 else 0
        best, bestv = [0, 0], -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): continue
            v = -(abs(nx - tx) + abs(ny - ty))
            if v > bestv: bestv, best = v, [dx, dy]
        return best

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def cell_value(x, y):
        best = -10**18
        for rx, ry in resources:
            sd = dist(x, y, rx, ry)
            od = dist(ox, oy, rx, ry)
            # prefer cells that are closer than opponent for valuable picks; also avoid being slow
            v = (od - sd) * 100 - sd
            if v > best: best = v
        return best

    best, bestv = [0, 0], -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny): continue
        v = cell_value(nx, ny)
        # small tie-break: keep moving toward currently best resource
        if resources:
            rx, ry = min(resources, key=lambda r: dist(sx, sy, r[0], r[1]))
            v -= 0.01 * dist(nx, ny, rx, ry)
        if v > bestv:
            bestv, best = v, [dx, dy]
    return best if legal(sx + best[0], sy + best[1]) else [0, 0]