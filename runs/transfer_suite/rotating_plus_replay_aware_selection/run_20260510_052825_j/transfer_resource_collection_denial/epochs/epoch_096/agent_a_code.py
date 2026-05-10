def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if len(p) == 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**9

    # Deterministic tie-break: sort resources
    res_list = []
    for r in resources:
        if len(r) == 2:
            rx, ry = r[0], r[1]
            if inb(rx, ry) and (rx, ry) not in obstacles:
                res_list.append((rx, ry))
    res_list.sort()

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            nx, ny = sx, sy

        # Compute best target value from this next position
        cur_best = -10**9
        for rx, ry in res_list:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # If opponent is already at least as close, heavily discourage (resource-denial matchup)
            penalty = 0
            if od <= sd:
                penalty = (sd - od) * 5 + 20  # ensure strong avoidance when contested
            # Prefer resources where we "win" the race; also prefer closer for us
            value = (od - sd) * 3 - sd + penalty
            # Reward immediate pickup
            if nx == rx and ny == ry:
                value += 200
            if value > cur_best:
                cur_best = value

        if cur_best > best_val:
            best_val = cur_best
            best_move = (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]