def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role_self = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role_self) or ("catcher" in role_self) or ("pursuing" in role_self)
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    corner_target = max(corners, key=lambda c: (abs(c[0] - ox) + abs(c[1] - oy)))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def min_obst_d(nx, ny):
        md = 10**9
        for (x, y) in obstacles:
            dx = x - nx
            if dx < 0:
                dx = -dx
            dy = y - ny
            if dy < 0:
                dy = -dy
            d = dx if dx > dy else dy
            if d < md:
                md = d
        return md if obstacles else 5

    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_opp = dist(nx, ny, ox, oy)
        d_corner = abs(nx - corner_target[0]) + abs(ny - corner_target[1])
        obst_d = min_obst_d(nx, ny)

        if is_pursuer:
            score = -d_opp * 10 + d_corner * 0.01 + obst_d * 0.2
        else:
            score = d_opp * 10 - d_corner * 0.5 + obst_d * 0.2

        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]