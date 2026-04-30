def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    rem = observation.get("remaining_resource_count", None)
    try:
        late = int(rem) <= 4 if rem is not None else False
    except:
        late = False

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx = 0 if ox == sx else (1 if ox > sx else -1)
        ty = 0 if oy == sy else (1 if oy > sy else -1)
        return [tx, ty]

    # Strategic change: pick a target that we can reach quickly AND that tends to be far for the opponent.
    best_t = resources[0]
    best_s = -10**18
    for r in resources:
        ds = cheb((sx, sy), r)
        do = cheb((ox, oy), r)
        # late-game: prioritize closing distance; otherwise emphasize denying opponent
        s = (do - ds) * (2 if not late else 1) + (-ds if late else -0.5 * ds) + (0.2 * (do - ds))
        if s > best_s:
            best_s, best_t = s, r

    tx, ty = best_t
    # Move to reduce our distance to the chosen target, while also not becoming closer to it than necessary for the opponent.
    best_m = (0, 0)
    best_v = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        myd = cheb((nx, ny), (tx, ty))
        opd = cheb((ox, oy), (tx, ty))
        v = (-myd) + (0.7 * (opd - myd)) + (0.15 * (opd - cheb((sx, sy), (tx, ty))))
        if v > best_v:
            best_v, best_m = v, (dx, dy)

    return [int(best_m[0]), int(best_m[1])]