def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
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
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    def cheb(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    target = min(resources, key=lambda p: cheb((mx, my), p))

    best_dxdy = (0, 0)
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not legal(nx, ny):
            continue
        # Distance to target after move
        dist_me = cheb((nx, ny), target)
        dist_opp = cheb((ox, oy), target)
        score = dist_opp - dist_me  # prefer moves reducing our distance relative to opponent
        if score > best_score:
            best_score = score
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]