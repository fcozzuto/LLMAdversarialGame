def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_score = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue
        dist = cheb(nx, ny, ox, oy)
        man = abs(nx - ox) + abs(ny - oy)

        if is_evader:
            # Maximize separation; tie-break by pushing toward the farthest corner from the pursuer.
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            corner_dist = 0
            for cx, cy in corners:
                d = cheb(nx, ny, cx, cy)
                if d > corner_dist:
                    corner_dist = d
            score = (dist, corner_dist, -man)
        else:
            # Minimize separation; tie-break by reducing manhattan distance.
            score = (-dist, -man, -nx - ny)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move