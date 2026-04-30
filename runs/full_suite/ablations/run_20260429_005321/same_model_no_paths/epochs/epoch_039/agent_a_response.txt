def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best_t = None
        best_gap = None
        for x, y in resources:
            ds = cheb(sx, sy, x, y)
            do = cheb(ox, oy, x, y)
            gap = ds - do
            if best_t is None or (gap < 0 and gap < best_gap) or (best_t is not None and best_gap is not None and gap < best_gap):
                if gap < 0:
                    best_t = (x, y)
                    best_gap = gap
                elif best_t is None:
                    best_t = (x, y)
                    best_gap = gap
        if best_t is None:
            # fallback: nearest resource to us
            best_t = min(resources, key=lambda xy: (cheb(sx, sy, xy[0], xy[1]), xy[0], xy[1]))
    else:
        best_t = (w // 2, h // 2)

    tx, ty = best_t

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_self = cheb(nx, ny, tx, ty)
        if resources:
            # also consider closest remaining resource overall
            d_all = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < d_all:
                    d_all = d
            d_res = d_all
        else:
            d_res = d_self
        d_opp = cheb(nx, ny, ox, oy)
        # Prefer: reduce resource distance, and keep away from opponent
        val = (-d_res) + 0.25 * d_opp
        # Tie-break deterministically: favor lower (tx,ty) distance then lexicographic move
        val2 = val - 1e-6 * d_self
        if val2 > best_val or (val2 == best_val and (dx, dy) < best_move):
            best_val = val2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]