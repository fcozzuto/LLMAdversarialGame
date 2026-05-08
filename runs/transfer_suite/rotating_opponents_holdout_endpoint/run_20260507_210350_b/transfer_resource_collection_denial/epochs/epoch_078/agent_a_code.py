def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if resources:
        best_t = None
        best_k = None
        for tx, ty in resources:
            ds = md(sx, sy, tx, ty)
            do = md(ox, oy, tx, ty)
            k = (do - ds, -ds, -(tx + ty), -md(tx, ty, w - 1, h - 1), tx, ty)
            if best_k is None or k > best_k:
                best_k = k
                best_t = (tx, ty)

        tx, ty = best_t
        deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        cur_d = md(sx, sy, tx, ty)
        candidates = []
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                nd = md(nx, ny, tx, ty)
                score = (cur_d - nd, -nd, -max(0, md(ox, oy, nx, ny) - 1), -(nx + ny))
                candidates.append((score, dx, dy, nd))
        if candidates:
            candidates.sort(reverse=True)
            return [int(candidates[0][1]), int(candidates[0][2])]

        # fallback if all blocked: allow stay or any in bounds (engine will reject by keeping position)
        best = (None, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h:
                nd = md(nx, ny, tx, ty)
                score = (-nd, dx, dy)
                if best[0] is None or score > best[0]:
                    best = (score, dx, dy)
        return [int(best[1]), int(best[2])]

    return [0, 0]