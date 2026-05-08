def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_target = None
    best_score = None
    # Prefer resources we can reach earlier than opponent; break ties deterministically by location.
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # if ds < do, strong; if ds == do, mild; if ds > do, penalize
        rel = do - ds
        score = (-rel * 10) + (ds * 3)
        key = (score, rx, ry)
        if best_score is None or key < (best_score[0], best_score[1], best_score[2]):
            best_score = key
            best_target = (rx, ry)

    rx, ry = best_target

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic order: prioritize moves that reduce our distance first, then reduce opponent distance, then tie-break by dx,dy.
    scored = []
    cur_ds = cheb(sx, sy, rx, ry)
    cur_do = cheb(ox, oy, rx, ry)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ns = cheb(nx, ny, rx, ry)
        nd = cheb(nx, ny, ox, oy)  # slight separation to avoid getting blocked by contest dynamics
        no = cur_do
        # prefer: smaller ns; then smaller (do - ns) meaning we become closer relative advantage; then keep separation
        rel = (no - ns)
        val = (ns, -rel, nd, dx, dy)
        scored.append((val, [dx, dy]))
    if not scored:
        return [0, 0]
    scored.sort(key=lambda t: t[0])
    return scored[0][1]