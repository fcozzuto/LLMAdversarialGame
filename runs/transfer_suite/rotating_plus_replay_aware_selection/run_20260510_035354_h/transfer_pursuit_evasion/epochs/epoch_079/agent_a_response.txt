def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_key = None

    def cornerness(x, y):
        return (1 if x in (0, w - 1) else 0) + (1 if y in (0, h - 1) else 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d = abs(nx - ox) + abs(ny - oy)
        # obstacle proximity penalty (prefer moves that don't "hug" obstacles)
        prox = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                tx, ty = nx + ax, ny + ay
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                    prox += 1

        # small tie-break nudges toward/away from center depending on role
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_dist = abs(nx - cx) + abs(ny - cy)

        if is_evader:
            score = d + 0.55 * cornerness(nx, ny) - 0.06 * prox - 0.05 * center_dist
        else:
            score = -d + 0.12 * cornerness(nx, ny) - 0.08 * prox + 0.02 * center_dist

        key = (-score, d, prox, center_dist, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best