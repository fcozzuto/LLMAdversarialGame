def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    opp = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(opp[0]), int(opp[1])

    targets = []
    for key in ("opponent_territory", "unclaimed_cells", "resources"):
        lst = observation.get(key) or []
        for p in lst:
            if p and len(p) >= 2:
                targets.append((int(p[0]), int(p[1])))
            if len(targets) >= 80:
                break
        if len(targets) >= 80:
            break

    def best_dist(x, y):
        if not targets:
            return abs(x - ox) + abs(y - oy)
        d = 10**9
        for tx, ty in targets:
            dd = abs(x - tx) + abs(y - ty)
            if dd < d:
                d = dd
        return d

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Prefer moving closer to targets; mildly prefer moving away from opponent.
        d = best_dist(nx, ny)
        move_away = abs(nx - ox) + abs(ny - oy)
        score = (-d) + 0.01 * move_away
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best

    # Fallback: deterministic safe step or stay.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            return [dx, dy]
    return [0, 0]