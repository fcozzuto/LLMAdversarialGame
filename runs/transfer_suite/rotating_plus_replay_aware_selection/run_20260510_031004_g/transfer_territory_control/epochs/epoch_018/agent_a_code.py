def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    resources = list(map(tuple, observation.get("resources", [])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_at(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        if resources:
            dmin = 10**9
            for rx, ry in resources:
                d = abs(rx - nx) + abs(ry - ny)
                if d < dmin:
                    dmin = d
            res_term = 50 - 5 * dmin
        else:
            res_term = 0
        center_term = -abs(cx - nx) - abs(cy - ny)
        opp_term = -2 * (abs(px - nx) + abs(py - ny))
        return res_term + 0.5 * center_term + 0.1 * opp_term

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            s = score_at(nx, ny)
            if s > best[0]:
                best = (s, dx, dy)

    return [int(best[1]), int(best[2])]