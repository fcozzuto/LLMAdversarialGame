def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    rset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                rset.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("pursuer" in self_role) or ("chaser" in self_role) or ("pursue" in self_role)
    minimize = is_pursuer

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    dxsgn = 0 if ox == sx else (1 if ox > sx else -1)
    dysgn = 0 if oy == sy else (1 if oy > sy else -1)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = [0, 0]
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in rset:
            nx, ny = sx, sy

        d = cheb(nx, ny, ox, oy)

        stepx = 0 if ox == nx else (1 if ox > nx else -1)
        stepy = 0 if oy == ny else (1 if oy > ny else -1)

        # Wall-run prevention: if our move points into an obstacle, penalize it.
        wall_pen = 0
        if stepx != 0 or stepy != 0:
            ax, ay = nx + stepx, ny + stepy
            if not inside(ax, ay) or (ax, ay) in rset:
                wall_pen += 5
            bx, by = nx + stepx * 2, ny + stepy * 2
            if inside(bx, by) and (bx, by) in rset:
                wall_pen += 2

        # Also lightly prefer moves that reduce opponent's potential escape corridor.
        # Compute neighbor obstacles around the next step toward opponent.
        corridor_pen = 0
        tx, ty = nx + dxsgn, ny + dysgn
        for ox2, oy2 in ((tx - 1, ty), (tx + 1, ty), (tx, ty - 1), (tx, ty + 1)):
            if 0 <= ox2 < w and 0 <= oy2 < h and (ox2, oy2) in rset:
                corridor_pen += 1

        dist_term = d
        key = dist_term * 100 + wall_pen * 10 + corridor_pen

        if best_key is None or (key < best_key if minimize else key > best_key):
            best_key = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]