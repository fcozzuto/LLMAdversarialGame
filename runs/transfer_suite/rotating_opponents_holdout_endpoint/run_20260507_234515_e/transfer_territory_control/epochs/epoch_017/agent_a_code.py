def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = (observation.get("opponent_position") or [w - 1, h - 1])

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    bestv = -10**18
    order = moves
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        v = 0
        if (nx, ny) in unclaimed:
            v += 50
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                ax, ay = nx + adx, ny + ady
                if inside(ax, ay) and (ax, ay) in unclaimed:
                    v += 8
        v -= 3 * sum(((nx + px, ny + py) in obstacles) for px, py in [(-1,0),(1,0),(0,-1),(0,1)])
        v -= max(0, 6 - dist(nx, ny, ox, oy))  # avoid getting too close to opponent
        if v > bestv:
            bestv = v
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best