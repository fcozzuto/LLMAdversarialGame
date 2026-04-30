def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not valid(sx, sy):
        for dx, dy in [(-1, -1),(0, -1),(1, -1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1),(0, -1),(1, -1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if resources:
        def min_res_dist(px, py):
            best = 10**9
            for rx, ry in resources:
                d = kdist(px, py, rx, ry)
                if d < best:
                    best = d
            return best

        best_move = [0, 0]
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            self_d = min_res_dist(nx, ny)
            opp_d = min_res_dist(ox, oy)
            val = (opp_d - self_d) * 1000 - self_d
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
        return best_move

    # No known resources: chase opponent
    best_move = [0, 0]
    best_d = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = kdist(nx, ny, ox, oy)
        if d < best_d:
            best_d = d
            best_move = [dx, dy]
    return best_move