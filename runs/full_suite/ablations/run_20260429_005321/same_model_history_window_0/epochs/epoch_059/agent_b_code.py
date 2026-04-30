def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    res = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_resource_d(nx, ny):
        md = 10**18
        for rx, ry in res:
            d = (rx - nx) * (rx - nx) + (ry - ny) * (ry - ny)
            if d < md:
                md = d
        return md

    if not res:
        best = None
        base_d = (sx - ox) * (sx - ox) + (sy - oy) * (sy - oy)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            score = (d - base_d) * 1000 - (abs(nx - w // 2) + abs(ny - h // 2))
            cand = (score, dx, dy)
            if best is None or cand > best:
                best = cand
        return [best[1], best[2]] if best is not None else [0, 0]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = best_resource_d(nx, ny)
        od = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        score = -d * 10 + od
        if best is None or (score, -dx, -dy) > best[0:3]:
            best = (score, dx, dy)
    return [best[1], best[2]] if best is not None else [0, 0]