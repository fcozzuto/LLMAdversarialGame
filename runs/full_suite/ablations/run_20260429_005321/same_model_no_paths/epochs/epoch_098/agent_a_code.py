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

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def sign(v):
        if v > 0: return 1
        if v < 0: return -1
        return 0

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Target selection: prefer resources we can reach earlier; break ties deterministically.
    if resources:
        best = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Higher is better: win potential first, then closer.
            score = (-(sd - od), -sd, (rx + 3 * ry))
            if best is None or score > best[0]:
                best = (score, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    dx0 = sign(tx - sx)
    dy0 = sign(ty - sy)

    candidates = []
    # Deterministically rank neighboring cells: mostly move toward target, avoid obstacles, then by distance.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        move_toward = -cheb(nx, ny, tx, ty)
        align = (dx, dy) == (dx0, dy0)
        candidates.append((align, move_toward, cheb(nx, ny, tx, ty), nx, ny, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(reverse=True)
    return [int(candidates[0][5]), int(candidates[0][6])]