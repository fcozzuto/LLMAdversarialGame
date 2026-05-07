def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def manh(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for t in resources:
        sd = manh((sx, sy), t)
        od = manh((ox, oy), t)
        # Prefer resources we can reach no later; else choose best relative race.
        key = (0 if sd <= od else 1, sd - od, sd, t[0], t[1])
        if best_key is None or key < best_key:
            best_key = key
            best = t
    tx, ty = best

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cur = (sx, sy)
    best_step = (0, 0)
    best_dist = cheb(cur, (tx, ty)) + 10

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = cheb((nx, ny), (tx, ty))
        # Tie-break deterministically: closer first, then smaller dx, then smaller dy.
        if nd < best_dist or (nd == best_dist and (abs(dx), abs(dy), dx, dy) < (abs(best_step[0]), abs(best_step[1]), best_step[0], best_step[1])):
            best_dist = nd
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]