def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res_set = set(tuple(p) for p in resources)
    if not resources:
        dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in res_set:
            val = 10**9
        else:
            md = 10**9
            for rx, ry in res_set:
                d = abs(nx - rx) + abs(ny - ry)
                if d < md:
                    md = d
            # Prefer moving closer to resources and slightly away from opponent
            val = -md - (abs(nx - ox) + abs(ny - oy)) * 0.001
        if val > best_val:
            best_val = val
            best = [dx, dy]

    if best is not None:
        return best
    return [0, 0]