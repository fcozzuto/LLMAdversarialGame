def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    best_t = None
    best_td = None
    for x, y in res:
        d = abs(x - sx) + abs(y - sy)
        if best_td is None or d < best_td or (d == best_td and (x, y) < best_t):
            best_td, best_t = d, (x, y)
    tx, ty = best_t

    deltas = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    bestm = [0, 0]
    bestkey = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        myd = abs(tx - nx) + abs(ty - ny)
        oppd = abs(tx - ox) + abs(ty - oy)
        advantage = oppd - myd  # larger is better

        # also softly prefer moves that reduce opponent access to the chosen target
        key = (-advantage, myd, abs(nx - ox) + abs(ny - oy), dx, dy)
        if bestkey is None or key < bestkey:
            bestkey = key
            bestm = [dx, dy]

    return bestm