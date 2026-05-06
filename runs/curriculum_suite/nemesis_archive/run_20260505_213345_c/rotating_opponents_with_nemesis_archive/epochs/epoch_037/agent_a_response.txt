def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
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

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_res(r):
        rx, ry = r
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # Prefer resources opponent is unlikely to reach quickly.
        # Also bias slightly toward nearer resources so we keep collecting.
        s = (d_me - d_op) * 10 - d_me
        # If far from the edge (more constrained), prioritize it a bit more.
        edge = min(rx, w - 1 - rx, ry, h - 1 - ry)
        s += edge * 0.2
        return s

    # If opponent is closer to most resources, do "block/shadow" by moving toward them.
    res_scores = sorted((score_res(r), r) for r in resources)
    best_target = res_scores[-1][1]
    opp_closest = min(resources, key=lambda r: cheb(ox, oy, r[0], r[1]))
    my_closest = min(resources, key=lambda r: cheb(sx, sy, r[0], r[1]))
    mode_block = cheb(ox, oy, opp_closest[0], opp_closest[1]) <= cheb(sx, sy, my_closest[0], my_closest[1])

    if mode_block and (observation.get("turn_index", 0) % 2 == 0):
        tx, ty = ox, oy
    else:
        tx, ty = best_target

    # Greedy step toward (tx,ty) with obstacle avoidance.
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            # Primary: reduce distance to target. Secondary: avoid moving adjacent to opponent when shadowing.
            d = cheb(nx, ny, tx, ty)
            adj_opp = cheb(nx, ny, ox, oy)  # 0 means same cell; others 1 means adjacent/near.
            val = d * 100 + adj_opp
            # Deterministic tie-break: lexicographic dx,dy
            tie = dx * 10 + dy
            val = val + tie * 0.001
            if best_val is None or val < best_val:
                best_val = val
                best = [dx, dy]

    return best if best is not None else [0, 0]