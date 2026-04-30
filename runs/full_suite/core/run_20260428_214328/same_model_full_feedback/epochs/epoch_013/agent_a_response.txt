def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**9

    res_set = set(resources)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in res_set:
            val = 10**6
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
            continue

        # Choose the resource we're "most likely" to reach from (nx, ny).
        # Then score the move by who can get it first (self advantage).
        closest = None
        closest_d = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < closest_d:
                closest_d = d
                closest = (rx, ry)

        rx, ry = closest
        self_d = closest_d
        opp_d = cheb(ox, oy, rx, ry)

        # Secondary terms:
        # - keep moving generally toward the resource cluster
        # - slightly avoid letting opponent get closer to us overall
        dist_to_opponent = cheb(nx, ny, ox, oy)
        val = (opp_d - self_d) * 1000 - self_d * 3 + dist_to_opponent

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move