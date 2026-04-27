def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist_cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_step(target, maximize_away=False):
        cand = []
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if not legal(nx, ny):
                continue
            d = dist_cheb((nx, ny), target)
            if maximize_away:
                d = -d
            cand.append((d, dx, dy))
        cand.sort()
        return cand[0][1], cand[0][2] if cand else (0, 0)

    if resources:
        target = min(resources, key=lambda r: (dist_cheb((mx, my), r), r[0], r[1]))
        dx, dy = best_step(target, maximize_away=False)
        return [dx, dy]
    else:
        target = (ox, oy)
        dx, dy = best_step(target, maximize_away=True)
        return [dx, dy]