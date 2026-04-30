def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    free = lambda x, y: inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    # Pick a resource where we are relatively closer than the opponent.
    best_r = None
    best_gain = -10**9
    for r in resources:
        dm = dist((sx, sy), r)
        do = dist((ox, oy), r)
        gain = do - dm  # positive means we are closer (or opponent farther)
        # tie-break deterministically toward nearer-than-opponent and then by coordinate
        if gain > best_gain or (gain == best_gain and (dm < dist((sx, sy), best_r) if best_r else True) or (gain == best_gain and best_r and r < best_r)):
            best_gain = gain
            best_r = r

    if not best_r:
        # No resources: try to increase separation from opponent while moving to center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        def center_score(x, y):
            return -abs(x - cx) - abs(y - cy)
        best = None
        for dx, dy, nx, ny in cand:
            sep = dist((nx, ny), (ox, oy))
            sc = sep * 2 + center_score(nx, ny)
            if best is None or sc > best[0] or (sc == best[0] and (dx, dy) < (best[1], best[2])):
                best = (sc, dx, dy)
        return [best[1], best[2]]

    # Move to reduce distance to the chosen target; also discourage moving into opponent pressure.
    target = best_r
    best = None
    for dx, dy, nx, ny in cand:
        d_me = dist((nx, ny), target)
        d_opp = dist((ox, oy), target)
        # extra pressure term: if opponent can reach target much sooner, we deprioritize.
        urgency = d_opp - d_me  # higher is better
        # safety: keep a bit of distance from opponent while approaching target
        safety = dist((nx, ny), (ox, oy))
        sc = urgency * 3 - d_me * 0.5 + safety * 0.05
        if best is None or sc > best[0] or (sc == best[0] and (dx, dy) < (best[1], best[2])):
            best = (sc, dx, dy)

    return [best[1], best[2]]