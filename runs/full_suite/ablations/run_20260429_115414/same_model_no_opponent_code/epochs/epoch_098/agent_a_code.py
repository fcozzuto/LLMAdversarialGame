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

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if in_bounds(x, y) and (x, y) not in obstacles:
                res.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (10**18, (0, 0))
    if res:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            md = min(abs(nx - rx) + abs(ny - ry) for rx, ry in res)
            od = abs(nx - ox) + abs(ny - oy)
            # Prefer smaller resource distance, then prefer being farther from opponent
            score = md * 1000 - od
            if score < best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
    else:
        # No resources: move away from opponent deterministically
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            od = abs(nx - ox) + abs(ny - oy)
            score = -od
            if score < best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))

    dx, dy = best[1]
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        dx, dy = 0, 0
    if not in_bounds(sx + dx, sy + dy) or (sx + dx, sy + dy) in obstacles:
        dx, dy = 0, 0
    return [int(dx), int(dy)]