def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = [(p[0], p[1]) for p in resources if p and len(p) >= 2]
    if not res:
        return [0, 0]
    obs = set((p[0], p[1]) for p in obstacles if p and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Value next cell by the best resource it can "win" against the opponent.
        # Higher is better: larger distance advantage; tie-break by smaller self distance;
        # slight preference toward board center.
        local_best = -10**18
        local_self = 10**9
        for rx, ry in res:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            val = (od - sd) * 1000 - sd
            if val > local_best or (val == local_best and sd < local_self):
                local_best = val
                local_self = sd

        center_pen = abs(nx - cx) + abs(ny - cy)
        total = local_best - center_pen * 0.01

        if total > best_val:
            best_val = total
            best_move = [dx, dy]

    return best_move