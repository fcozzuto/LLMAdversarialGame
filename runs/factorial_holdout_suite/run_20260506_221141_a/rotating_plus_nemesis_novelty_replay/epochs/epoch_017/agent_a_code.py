def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = int(observation.get("grid_width", 8))
    gh = int(observation.get("grid_height", 8))

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < gw and 0 <= y < gh:
                obs.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < gw and 0 <= y < gh and (x, y) not in obs:
                resources.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def ok(x, y):
        return 0 <= x < gw and 0 <= y < gh and (x, y) not in obs

    if resources:
        best = None
        for rx, ry in resources:
            ds = abs(rx - sx) + abs(ry - sy)
            do = abs(rx - ox) + abs(ry - oy)
            score = (do - ds) * 1000 - ds
            if best is None or score > best[0] or (score == best[0] and ds < best[1]):
                best = (score, ds, rx, ry)
        tx, ty = best[2], best[3]
    else:
        tx, ty = gw // 2, gh // 2

    best_move = [0, 0]
    best_dist = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        if best_dist is None or dist < best_dist or (dist == best_dist and (dx, dy) > tuple(best_move)):
            best_dist = dist
            best_move = [dx, dy]

    return best_move