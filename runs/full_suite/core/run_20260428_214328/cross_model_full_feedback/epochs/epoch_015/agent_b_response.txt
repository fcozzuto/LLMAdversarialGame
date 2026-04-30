def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles_list = observation.get("obstacles", []) or []
    resources_list = observation.get("resources", []) or []

    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_list)
    resources = [(int(p[0]), int(p[1])) for p in resources_list]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def collide(x, y):
        return (x, y) in obstacles or (x, y) == (ox, oy)

    def dist(a, b):
        ax, ay = a; bx, by = b
        return max(abs(ax - bx), abs(ay - by))

    # Compile candidate resources near us (ignore far ones)
    if resources:
        best_res = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or collide(nx, ny):
                continue
            # distance to nearest resource from (nx,ny)
            d = None
            for rx, ry in resources:
                if not inside(rx, ry) or (rx, ry) in obstacles:
                    continue
                d2 = dist((nx, ny), (rx, ry))
                if d is None or d2 < d:
                    d = d2
            if d is None:
                continue
            # prefer closer resource, then safer from opponent
            oppd = dist((nx, ny), (ox, oy))
            score = (d, oppd)
            if best_score is None or score < best_score:
                best_score = score
                best_res = (dx, dy)
        if best_res is not None:
            return [best_res[0], best_res[1]]

    # Fallback: move away from opponent when possible, otherwise toward center/resource or stay
    best = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles or (nx, ny) == (ox, oy):
            continue
        # prefer positions with greater distance from opponent
        d = dist((nx, ny), (ox, oy))
        # small penalty for lingering near edges: keep simple
        score = d
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]

    return [0, 0]