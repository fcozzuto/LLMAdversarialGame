def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    def move_ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    opp_target_bias = 2  # favor contested resources we can reach
    best_t = None
    best_key = None
    for (rx, ry) in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (ds - (opp_target_bias / (1 + do)), ds, -do)  # deterministic float via /; still deterministic
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not move_ok(nx, ny):
            continue
        my_dist = cheb(nx, ny, tx, ty)
        opp_dist = cheb(ox, oy, tx, ty)
        same_target_pressure = -0.35 * (my_dist - cheb(sx, sy, tx, ty))
        contest = 0.0
        if opp_dist <= my_dist:
            contest = 0.25  # prefer moves that keep us ahead; higher score is worse
        # small preference for reducing opponent distance to us (denier-like)
        opp_to_me = cheb(ox, oy, nx, ny)
        block = 0.02 * opp_to_me
        score = (my_dist, contest, block)  # lexicographic: minimize my_dist, then contest, then block
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]