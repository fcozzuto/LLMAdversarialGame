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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx = w - 1 if ox > sx else 0
        ty = h - 1 if oy > sy else 0
        best = (10**9, 10**9, None)
        for tx2, ty2 in [(tx, ty)]:
            for dx, dy in dirs:
                nx, ny = sx + dx, sy + dy
                if not legal(nx, ny): 
                    continue
                d = cheb(nx, ny, tx2, ty2)
                cand = (d, cheb(nx, ny, ox, oy), (dx, dy))
                if cand < best: best = cand
        return best[2] if best[2] is not None else [0, 0]

    # Pick a contest target: minimize (my distance, opponent distance), prefer my lead.
    resources_sorted = sorted(resources, key=lambda t: (t[0], t[1]))
    best_target = None
    best_key = None
    for tx, ty in resources_sorted:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        lead = myd - opd  # negative is good
        key = (lead, myd, opd, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (tx, ty)

    tx, ty = best_target
    best_move = None
    best_move_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        myd_next = cheb(nx, ny, tx, ty)
        opd_next = cheb(ox, oy, tx, ty)
        # Also slightly prefer moves that reduce opponent's ability to contest nearby.
        contest_penalty = 0
        for rx, ry in resources_sorted[: min(6, len(resources_sorted))]:
            if (rx, ry) != (tx, ty):
                contest_penalty += 1 if cheb(ox, oy, rx, ry) <= cheb(nx, ny, rx, ry) else 0
        key = (myd_next, cheb(nx, ny, ox, oy), myd_next - opd_next, contest_penalty, dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])] if best_move is not None else [0, 0]