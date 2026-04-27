def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    if resources:
        best = None
        best_score = 10**9
        for rx, ry in resources:
            dme = cheb((mx, my), (rx, ry))
            dop = cheb((ox, oy), (rx, ry))
            score = dme + dop
            if score < best_score:
                best_score = score
                best = (rx, ry)
        if best is not None:
            tx, ty = best
            best_dx = 0
            best_dy = 0
            best_dist = 10**9
            for dx, dy in moves:
                nx, ny = mx + dx, my + dy
                if not in_bounds(nx, ny):
                    continue
                d = cheb((nx, ny), (tx, ty))
                if d < best_dist:
                    best_dist = d
                    best_dx, best_dy = dx, dy
            return [best_dx, best_dy]

    # No resources: move toward center to minimize risk and approach midpoints
    tx, ty = (w - 1) // 2, (h - 1) // 2
    best_dx, best_dy = 0, 0
    best_dist = 10**9
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not in_bounds(nx, ny):
            continue
        d = cheb((nx, ny), (tx, ty))
        if d < best_dist:
            best_dist = d
            best_dx, best_dy = dx, dy
    return [best_dx, best_dy]