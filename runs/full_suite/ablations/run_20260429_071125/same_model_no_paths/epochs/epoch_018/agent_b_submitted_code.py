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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inside(x, y):
                resources.append((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        cx, cy = w // 2, h // 2
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                score = man(nx, ny, ox, oy)
                score = (score << 20) - man(nx, ny, cx, cy)
                if best is None or score > best_score or (score == best_score and (dx, dy) < best):
                    best, best_score = (dx, dy), score
        return [best[0], best[1]] if best is not None else [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dmin = 10**9
        for rx, ry in resources:
            d = man(nx, ny, rx, ry)
            if d < dmin:
                dmin = d
        opp = man(nx, ny, ox, oy) if inside(ox, oy) else 0
        score = (-dmin << 20) + opp  # closer to resources, farther from opponent
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best, best_score = (dx, dy), score

    if best is None:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [int(best[0]), int(best[1]]]