def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    candidates = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    candidates = sorted(candidates, key=lambda t: (abs(t[0]) + abs(t[1]), t[0], t[1]))

    best = None
    best_move = (0, 0)

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if not resources:
            val = (0, -cheb(nx, ny, ox, oy), nx + ny)
        else:
            # Denial-aware: prefer cells that make opponent farther than us to the same resource.
            best_res = None
            for rx, ry in resources:
                if (rx, ry) in obs:
                    continue
                selfd = cheb(nx, ny, rx, ry)
                oppd = cheb(ox, oy, rx, ry)
                val = (oppd - selfd, -selfd, -abs(rx - ox) - abs(ry - oy), rx + ry)
                if best_res is None or val > best_res:
                    best_res = val
            val = best_res
        if best is None or val > best:
            best = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]