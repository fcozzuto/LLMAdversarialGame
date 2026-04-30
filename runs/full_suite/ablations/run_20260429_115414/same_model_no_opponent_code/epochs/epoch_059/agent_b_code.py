def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        res = [(w // 2, h // 2)]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy
        # For this next position, pick the resource you can reach sooner than the opponent.
        best_adv = None
        best_dself = None
        for rx, ry in res:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            adv = do - ds
            if best_adv is None or adv > best_adv or (adv == best_adv and (best_dself is None or ds < best_dself)) or \
               (adv == best_adv and ds == best_dself and (rx < res[0][0] or (rx == res[0][0] and ry < res[0][1]))):
                best_adv = adv
                best_dself = ds
        # Prefer positive advantage strongly; then closeness to that resource; lightly avoid giving the opponent shortcuts.
        opp_closer = min(dist(nx, ny, rx, ry) - dist(ox, oy, rx, ry) for (rx, ry) in res)
        score = (best_adv * 100) - best_dself + (-opp_closer)
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
        elif score == best_score:
            if (dx, dy) < best:
                best = (dx, dy)

    return [int(best[0]), int(best[1])]