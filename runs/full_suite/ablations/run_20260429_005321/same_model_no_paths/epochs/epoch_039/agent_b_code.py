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
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = [(dx, dy) for dx, dy in dirs if inside(sx + dx, sy + dy)]
    if not valid:
        return [0, 0]

    if resources:
        res_list = resources[:]
        # choose target by "who can get it first" with deterministic tie-breaking
        scored = []
        for i, (x, y) in enumerate(res_list):
            ds = cheb(sx, sy, x, y)
            do = cheb(ox, oy, x, y)
            # prefer resources that we can reach sooner, otherwise second-best
            gain = (do - ds)
            # small deterministic bias to avoid ties bouncing
            bias = -0.001 * (x + 3 * y + i)
            scored.append((gain + bias, ds, do, x, y))
        scored.sort(key=lambda t: (-t[0], t[1], t[2], t[3], t[4]))
        tx, ty = scored[0][3], scored[0][4]
    else:
        # deterministic fallback: go toward center-ish but away from opponent
        tx, ty = w // 2, h // 2

    best = None
    bestv = -10**18
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        d_to = cheb(nx, ny, tx, ty)
        d_from = cheb(ox, oy, tx, ty)
        # also steer away from opponent to reduce contest
        d_opp = cheb(nx, ny, ox, oy)
        # and avoid moving closer to opponent when contesting
        v = -d_to + 0.10 * d_opp + 0.05 * (d_from - cheb(ox, oy, tx, ty))
        # if target is contested, strongly favor moves that make us closer than opponent
        ds_now = cheb(nx, ny, tx, ty)
        do_now = cheb(ox, oy, tx, ty)
        v += 2.0 if ds_now <= do_now else 0.0
        if best is None or v > bestv:
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]