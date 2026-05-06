def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist_cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        # Choose a target that we can reach not much slower than opponent; otherwise pick nearest resource.
        best = None
        best_score = None
        for rx, ry in resources:
            ds = dist_cheb(sx, sy, rx, ry)
            do = dist_cheb(ox, oy, rx, ry)
            score = (ds - do, ds)  # lexicographic
            if best is None or score < best_score:
                best = (rx, ry)
                best_score = score
        tx, ty = best
    else:
        tx, ty = w // 2, h // 2

    chosen = (0, 0)
    chosen_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        val = dist_cheb(nx, ny, tx, ty)
        if chosen_val is None or val < chosen_val:
            chosen_val = val
            chosen = (dx, dy)
    return [int(chosen[0]), int(chosen[1])]