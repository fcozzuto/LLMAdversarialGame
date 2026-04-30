def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_move(nx, ny):
        # If resources exist: contest best target by maximizing (opponent farther) while getting closer.
        if resources:
            # Pick a small deterministic set of candidate targets: closest by my distance then tie by coordinates.
            res_sorted = sorted(resources, key=lambda r: (cheb(nx, ny, r[0], r[1]), r[0], r[1]))
            best = -10**18
            k = 6 if len(res_sorted) > 6 else len(res_sorted)
            for i in range(k):
                tx, ty = res_sorted[i]
                myd = cheb(nx, ny, tx, ty)
                opd = cheb(ox, oy, tx, ty)
                # Large weight to deny opponent; slight penalty to avoid long routes.
                v = (opd - myd) * 12 - myd
                # If we could step onto a resource, strongly prefer.
                if myd == 0:
                    v += 10**6
                # If opponent already at the resource, discourage.
                if opd == 0:
                    v -= 10**6
                # Prefer also being closer to the same target than staying.
                if v > best:
                    best = v
            return best
        # No resources: move toward center while keeping away from obstacles implicitly by valid().
        cx, cy = (w - 1) // 2, (h - 1) // 2
        d = cheb(nx, ny, cx, cy)
        return -d + (cheb(nx, ny, ox, oy) * 0.1)

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        v = score_move(nx, ny)
        # Deterministic tie-break: lexicographic preference on (dx,dy) then higher score.
        if v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]