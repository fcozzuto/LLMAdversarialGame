def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    res_sorted = sorted(resources, key=lambda r: cheb(sx, sy, r[0], r[1]))
    top = res_sorted[:6]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        score = 0
        if (nx, ny) in resources:
            score += 10**6

        # Aim for resources where we are closer than opponent; otherwise deny by approaching.
        for rx, ry in top:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer being closer; also prefer reducing distance to contested targets.
            contest = do - ds
            score += contest * 120 - ds * 8

        # Keep distance from opponent unless it helps contesting.
        dpo = cheb(nx, ny, ox, oy)
        score -= dpo * 2

        # Mild obstacle/boundary pressure to avoid dead-ends.
        if nx == 0 or nx == w - 1: score -= 30
        if ny == 0 or ny == h - 1: score -= 30

        if score > best_score:
            best_score = score
            best = [dx, dy]
        elif score == best_score and best is not None:
            if (dx, dy) < (best[0], best[1]):
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return best