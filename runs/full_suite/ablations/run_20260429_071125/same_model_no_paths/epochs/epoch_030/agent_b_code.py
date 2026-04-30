def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    res_list = observation.get("resources") or []
    resources = []
    for r in res_list:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not ok(sx, sy):
        for dx, dy in moves:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_move = [0, 0]
    best_val = -10**9

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            dfo = cheb(nx, ny, ox, oy)
            val = dfo  # maximize distance from opponent
            if val > best_val or (val == best_val and (dx, dy) < tuple(best_move)):
                best_val = val
                best_move = [dx, dy]
        return best_move

    # Find a target resource deterministically: closest, then lowest (x,y)
    target = min(resources, key=lambda p: (cheb(sx, sy, p[0], p[1]), p[1], p[0]))
    tx, ty = target

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dcur = cheb(sx, sy, tx, ty)
        dnew = cheb(nx, ny, tx, ty)
        # Prefer reducing distance to target; discourage getting closer to opponent
        dopp_new = cheb(nx, ny, ox, oy)
        val = (dcur - dnew) * 1000 + dnew * -2 + dnew  # keep slight preference for nearer
        val += dopp_new * 3
        if val > best_val or (val == best_val and (dx, dy) < tuple(best_move)):
            best_val = val
            best_move = [dx, dy]

    return best_move