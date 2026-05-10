def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if p and len(p) >= 2)

    unclaimed = observation.get("unclaimed_cells", []) or []
    un = [(p[0], p[1]) for p in unclaimed if p and len(p) >= 2 and 0 <= p[0] < w and 0 <= p[1] < h]

    resources = observation.get("resources", []) or []
    res = [(p[0], p[1]) for p in resources if p and len(p) >= 2 and 0 <= p[0] < w and 0 <= p[1] < h]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_target(cells, fallback):
        if cells:
            tx, ty = min(cells, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
            return tx, ty
        return fallback

    target = best_target(un, (w // 2, h // 2))
    if target == (w // 2, h // 2) and not un and res:
        target = best_target(res, target)

    tx, ty = target
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_t = abs(nx - tx) + abs(ny - ty)
        d_o = abs(nx - ox) + abs(ny - oy)
        # Prefer closeness to target, avoid opponent, prefer unclaimed if available
        bonus = 0
        if (nx, ny) in set(un) if un else False:
            bonus += 6
        score = -d_t + 0.4 * min(d_o, 8) + bonus
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best = (dx, dy)
            best_score = score

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]