def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    cx, cy = (w - 1) // 2, (h - 1) // 2
    opp = (ox, oy)
    me = (sx, sy)

    # If no resources, move to center while keeping distance from opponent.
    if not resources:
        best = None
        best_score = -10**18
        for dx, dy in legal:
            nm = (sx + dx, sy + dy)
            score = (man(nm, opp) * 2) - (man(nm, (cx, cy)))
            if score > best_score:
                best_score, best = score, (dx, dy)
        return [int(best[0]), int(best[1])]

    # Score each move by winning contention for the best resource.
    # Use max over resources: prefer moves where we reach some resource significantly earlier than opponent.
    best = None
    best_score = -10**18
    for dx, dy in legal:
        nm = (sx + dx, sy + dy)
        center_bias = -man(nm, (cx, cy)) * 0.05
        opp_block = 0.0
        if man(nm, opp) == 0:
            opp_block -= 5.0
        best_over_resources = -10**18
        for tr in resources:
            dm = man(nm, tr)
            do = man(opp, tr)
            # positive if we can arrive earlier; also prefer closer win even if both can reach.
            contention = (do - dm) * 1.5
            tie_favor = 0.25 if dm < do else (0.05 if dm == do else 0.0)
            # slight preference for nearer resources overall.
            proximity = -dm * 0.08
            score_tr = contention + tie_favor + proximity
            if score_tr > best_over_resources:
                best_over_resources = score_tr
        # small deterministic tiebreaker: favor lexicographically smaller move
        score = best_over_resources + center_bias + opp_block
        if score > best_score:
            best_score, best = score, (dx, dy)
        elif score == best_score and best is not None:
            if (dx, dy) < best:
                best = (dx, dy)

    return [int(best[0]), int(best[1])]