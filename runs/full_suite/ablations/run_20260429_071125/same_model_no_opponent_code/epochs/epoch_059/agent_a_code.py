def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        # Defensive fallback: move to maximize separation while staying valid
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = abs(nx - ox) + abs(ny - oy)
            v = d
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    my = (sx, sy)
    opp = (ox, oy)

    # Choose a contested target: prefer resources where we are not behind and can get them soon
    best_t = None
    best_key = (-10**9, -10**9)
    for r in resources:
        dm = manhattan(my, r)
        do = manhattan(opp, r)
        key1 = (do - dm)  # advantage; positive means we are closer
        key2 = -dm          # smaller dm preferred
        if key1 > best_key[0] or (key1 == best_key[0] and key2 > best_key[1]):
            best_key = (key1, key2)
            best_t = r
    tx, ty = best_t

    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ndm = abs(nx - tx) + abs(ny - ty)
        ndo = abs(nx - ox) + abs(ny - oy)
        # Primary: reduce distance to target; Secondary: increase distance from opponent; Tertiary: keep moving (avoid pointless stalls)
        v = (-ndm) * 100 + (ndo) * 2 - (1 if (dx == 0 and dy == 0) else 0)
        if v > bestv:
            bestv, best = v, (dx, dy)
    return [int(best[0]), int(best[1])]