def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obst = observation.get("obstacles", [])
    obstacles = set((p[0], p[1]) for p in obst)

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def in_bounds(x, y): return 0 <= x < w and 0 <= y < h
    def d2(a, b):
        dx = a[0] - b[0]; dy = a[1] - b[1]
        return dx*dx + dy*dy

    if not resources:
        tx, ty = w//2, h//2
        best = None
        for dx, dy in moves:
            nx, ny = sx+dx, sy+dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                score = d2((nx, ny), (tx, ty))
                if best is None or score < best[0]:
                    best = (score, dx, dy)
        if best is None:
            for dx, dy in moves:
                nx, ny = sx+dx, sy+dy
                if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                    return [dx, dy]
            return [0, 0]
        return [best[1], best[2]]

    target = None
    best_t = None
    for rx, ry in resources:
        dm = d2((sx, sy), (rx, ry))
        do = d2((ox, oy), (rx, ry))
        score = dm - 0.35 * do
        if best_t is None or score < best_t:
            best_t = score
            target = (rx, ry)

    best = None
    for dx, dy in moves:
        nx, ny = sx+dx, sy+dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        score = d2((nx, ny), target) + 0.03 * d2((nx, ny), (ox, oy))
        if best is None or score < best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]