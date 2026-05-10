def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    opp_dist_curr = cheb(ox, oy, sx, sy)

    oy_bias = [r for r in resources if r[1] != oy]
    cand = oy_bias if oy_bias else resources

    # Score: win the race to resource; larger is better.
    best = None
    best_score = None
    for x, y in cand:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        off = 1 if y != oy else 0
        score = (do - ds) * 100 + off * 3 - ds
        if best_score is None or score > best_score or (score == best_score and ds < best[0]):
            best_score = score
            best = (ds, x, y)

    _, tx, ty = best
    if tx == sx and ty == sy:
        return [0, 0]

    # Greedy local move: among valid neighbor deltas, pick the one that best improves target distance.
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]
    best_d = (0, 0)
    best_m = None
    curd = cheb(sx, sy, tx, ty)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # prefer reaching sooner; slight bias to avoid opponent sweep by not matching their row
        m = (curd - nd) * 100 + (1 if ny != oy else 0) * 2
        if best_m is None or m > best_m or (m == best_m and nd < cheb(sx, sy, tx, ty)):
            best_m = m
            best_d = (dx, dy)

    return [int(best_d[0]), int(best_d[1])]