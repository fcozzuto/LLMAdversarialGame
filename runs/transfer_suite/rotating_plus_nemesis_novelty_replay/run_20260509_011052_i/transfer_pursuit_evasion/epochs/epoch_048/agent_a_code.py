def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in self_role) and ("evader" not in self_role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        m = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                m += 1
        return m

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    corner_x, corner_y = (w - 1, h - 1)
    if corners:
        if pursuer:
            target_corner = min(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        else:
            target_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        corner_x, corner_y = target_corner

    best = None
    best_score = -10**18 if pursuer else 10**18

    # If resources exist, bias toward nearest (pursuer) / farthest (evader) resource deterministically.
    if resources:
        if pursuer:
            rx, ry = min(resources, key=lambda p: cheb(sx, sy, p[0], p[1]))
        else:
            rx, ry = max(resources, key=lambda p: cheb(sx, sy, p[0], p[1]))
    else:
        rx, ry = None, None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        # corner bias: pursuer wants move that reduces opponent distance; evader wants far corners.
        corner_d = cheb(nx, ny, corner_x, corner_y)
        # resource bias as a weak term if present.
        if rx is not None:
            res_d = cheb(nx, ny, rx, ry)
        else:
            res_d = 0

        if pursuer:
            score = -d + 0.08 * mob + 0.01 * (-corner_d) + (0.02 * (-res_d))
            # keep deterministic preference order via small additional term
        else:
            score = d + 0.08 * mob + 0.01 * (corner_d) + (0.02 * (res_d))

        if pursuer:
            if score > best_score:
                best_score = score
                best = [dx, dy]
        else:
            if score < best_score:
                best_score = score
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]