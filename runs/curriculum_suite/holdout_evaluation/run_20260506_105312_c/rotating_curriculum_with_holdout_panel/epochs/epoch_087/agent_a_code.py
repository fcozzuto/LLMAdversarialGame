def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = observation.get("resources") or []
    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                targets.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    if targets:
        # Greedy toward nearest resource; slight preference to moves that reduce opponent distance less.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d_self = min(abs(nx - tx) + abs(ny - ty) for (tx, ty) in targets)
            d_opp = abs(nx - ox) + abs(ny - oy)
            score = (-(d_self * 10 + d_opp), -d_self)
            if best_score is None or score > best_score:
                best_score, best = score, [dx, dy]
    else:
        # No visible resources: move toward opponent if possible, else toward center-ish.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx, ty = ox, oy if abs(ox - sx) + abs(oy - sy) > 0 else (cx, cy)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            score = -(abs(nx - tx) + abs(ny - ty))
            if best_score is None or score > best_score:
                best_score, best = score, [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]