def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    w = int(w); h = int(h)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if in_bounds(x, y):
                resources.append((x, y))
    if not resources:
        return [0, 0]

    best_t = resources[0]
    best_val = -10**18
    best_my_d = 10**18
    for tx, ty in resources:
        my_d = cheb(sx, sy, tx, ty)
        op_d = cheb(ox, oy, tx, ty)
        val = (op_d - my_d) * 1000000 - my_d
        if val > best_val or (val == best_val and my_d < best_my_d):
            best_val = val
            best_my_d = my_d
            best_t = (tx, ty)

    tx, ty = best_t
    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best_m = (0, 0)
    best_md = 10**18
    best_op_dist = -1
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        md = cheb(nx, ny, tx, ty)
        opd = cheb(nx, ny, ox, oy)
        if md < best_md or (md == best_md and opd > best_op_dist):
            best_md = md
            best_op_dist = opd
            best_m = (dx, dy)
    return [int(best_m[0]), int(best_m[1])]