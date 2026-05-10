def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((int(p[0]), int(p[1])) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    res = [(int(p[0]), int(p[1])) for p in resources]
    if not res:
        return [0, 0]

    # Score a position by the best "race win" against the opponent for any resource.
    def best_value(px, py):
        best = None
        for rx, ry in res:
            myd = cheb(px, py, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Strongly prefer resources where we are closer; otherwise reduce.
            v = (opd - myd) * 1000 + (opd - myd) * 10 - myd
            if best is None or v > best[0] or (v == best[0] and myd < best[1]):
                best = (v, myd)
        return best[0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (float("-inf"), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = best_value(nx, ny)
        # Small tie-break: stay closer to opponent-competitiveness; also prefer forward progress.
        oppd = cheb(nx, ny, ox, oy)
        v2 = v - oppd * 0.01 - (abs(dx) + abs(dy)) * 0.001
        if v2 > best_move[0]:
            best_move = (v2, dx, dy)
    return [int(best_move[1]), int(best_move[2])]