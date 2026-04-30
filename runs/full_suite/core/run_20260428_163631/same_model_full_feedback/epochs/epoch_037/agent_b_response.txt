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

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        best = (0, 0, -10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            score = cheb(nx, ny, ox, oy)
            if score > best[2]:
                best = (dx, dy, score)
        return [best[0], best[1]]

    # Pick a primary target: prefer nearest to self; if opponent is closer to a resource, bias toward contested ones.
    best_res = None
    best_tag = -10**9
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        tag = -ds + (1.5 if do <= ds else 0.0)  # contest bonus
        if tag > best_tag:
            best_tag = tag
            best_res = (rx, ry)

    tx, ty = best_res

    # Secondary: opponent's nearest resource (to reduce its progress)
    best_op = None
    best_do = 10**9
    for rx, ry in resources:
        do = cheb(ox, oy, rx, ry)
        if do < best_do:
            best_do = do
            best_op = (rx, ry)
    ox2, oy2 = best_op

    best_move = (0, 0, -10**9)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(nx, ny, ox2, oy2)
        opp_dist = cheb(nx, ny, ox, oy)
        # Also slight term: prefer moving closer to self target while keeping away from opponent
        score = (-ds2 * 2.0) + (do2 * -0.2) + (opp_dist * 0.1)
        if score > best_move[2]:
            best_move = (dx, dy, score)

    return [int(best_move[0]), int(best_move[1])]