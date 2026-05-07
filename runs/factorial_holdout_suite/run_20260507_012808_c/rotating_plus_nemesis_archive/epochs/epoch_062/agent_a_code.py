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
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                if (x, y) not in obstacles:
                    resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # If any resource adjacent/at us, take deterministically (prefer immediate).
    immediate = []
    for x, y in resources:
        if cheb(sx, sy, x, y) == 0:
            immediate.append((0, x, y))
        elif cheb(sx, sy, x, y) == 1:
            immediate.append((1, x, y))
    if immediate:
        immediate.sort(key=lambda t: (t[0], cheb(ox, oy, t[1], t[2])))
        _, tx, ty = immediate[0]
    else:
        # Score: we want closer-than-opponent targets, but also strong candidates when behind.
        # Key favors: smaller (our_dist - 0.9*opp_dist); then our_dist; then opp_dist.
        best = None
        for x, y in resources:
            ds = cheb(sx, sy, x, y)
            do = cheb(ox, oy, x, y)
            comp = ds - 0.9 * do
            key = (comp, ds, do, x, y)
            if best is None or key < best[0]:
                best = (key, x, y)
        tx, ty = best[1], best[2]

    best_move = (10**9, -10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(nx, ny, ox, oy)
        # Minimize distance to target; maximize distance to opponent (avoid getting contested).
        key = (ns, -no, x := nx, y := ny)
        cand = (key[0], key[1], dx, dy)
        if cand < best_move:
            best_move = cand
    return [int(best_move[2]), int(best_move[3])]