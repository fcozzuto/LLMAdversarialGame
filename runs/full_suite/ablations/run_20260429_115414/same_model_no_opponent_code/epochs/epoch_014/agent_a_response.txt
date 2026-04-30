def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    rs = []
    for x, y in resources:
        x, y = int(x), int(y)
        if free(x, y):
            rs.append((x, y))
    if not rs:
        rs = [(w - 1, h - 1)] if free(w - 1, h - 1) else [(0, 0)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                moves.append((dx, dy))

    def obstacle_pressure(x, y):
        # small penalty for being adjacent to obstacles (encourages smoother routes)
        p = 0
        for ox2, oy2 in obs:
            if abs(ox2 - x) <= 1 and abs(oy2 - y) <= 1:
                if ox2 == x and oy2 == y:
                    p += 5
                else:
                    p += 1
        return p

    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # Materially different targeting: prefer resources that we can reach fast (min sd),
        # and avoid letting the opponent be strictly closer (prefer larger (sd-od)).
        cand_best_key = None
        for rx, ry in rs:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            reach_gap = sd - od  # negative means we are closer
            # Key to maximize: (avoid being behind), then get closer, then reduce opponent closeness
            key = (reach_gap, -sd, -od, -(rx + ry), -rx, -ry)
            if cand_best_key is None or key > cand_best_key:
                cand_best_key = key
        # Overall move preference: maximize best resource key, minus obstacle pressure
        oxp = obstacle_pressure(nx, ny)
        score = (cand_best_key[0] * 1000 + cand_best_key[1] * 10 + cand_best_key[2] - oxp)
        if best is None or score > best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]