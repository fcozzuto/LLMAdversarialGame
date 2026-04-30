def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (None, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        move_best = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we improve our lead; discourage moving into worse positions.
            score = (do - ds) * 100 - ds
            # Slightly prefer reducing distance to closest remaining resource overall
            score -= (cheb(nx, ny, sx, sy) * 0)  # deterministic no-op
            if rx == sx and ry == sy:
                score += 10000
            if score > move_best:
                move_best = score
        if move_best > best[1]:
            best = ((dx, dy), move_best)
        elif move_best == best[1] and best[0] is not None:
            # Deterministic tie-break: smallest |dx|+|dy|, then lexicographic
            cand = (dx, dy)
            cur = best[0]
            if abs(cand[0]) + abs(cand[1]) < abs(cur[0]) + abs(cur[1]) or (abs(cand[0]) + abs(cand[1]) == abs(cur[0]) + abs(cur[1]) and cand < cur):
                best = (cand, move_best)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]