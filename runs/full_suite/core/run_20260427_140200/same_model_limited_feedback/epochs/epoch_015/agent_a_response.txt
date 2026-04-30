def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(x, lo, hi): 
        return lo if x < lo else hi if x > hi else x

    def valid(x, y):
        if x < 0 or y < 0 or x >= w or y >= h: 
            return False
        if (x, y) in obstacles: 
            return False
        return True

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx*dx + dy*dy)

    # If no resources, just drift toward opponent to contest
    if not resources:
        tx, ty = ox, oy
        best = (10**18, [0, 0])
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            score = dist((nx, ny), (tx, ty))
            if score < best[0]:
                best = (score, [dx, dy])
        return best[1]

    # Choose a target that we can get to earlier than opponent (blocking/contesting)
    best_r = resources[0]
    best_adv = -10**18
    for r in resources:
        dsu = dist((sx, sy), r)
        dso = dist((ox, oy), r)
        adv = dso - dsu  # positive means we are closer
        # Slightly prefer nearer resources to reduce starvation
        pref = adv * 1000 - dsu
        if pref > best_adv:
            best_adv = pref
            best_r = r

    # Greedy model of opponent's response: move toward same target resource
    def opp_next(px, py):
        cur = (px, py)
        best = (10**18, (px, py))
        for dx, dy in deltas:
            nx, ny = px + dx, py + dy
            if not valid(nx, ny):
                continue
            sc = dist((nx, ny), best_r)
            if sc < best[0]:
                best = (sc, (nx, ny))
        return best[1]

    opnx, opny = opp_next(ox, oy)

    # Evaluate our moves: reduce distance to target, and increase distance between opponent and target
    best_move = [0, 0]
    best_val = 10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_us = dist((nx, ny), best_r)
        d_op = dist((opnx, opny), best_r)
        # Also consider stealing any resource closer for us
        steal = 0
        for r in resources:
            if dist((nx, ny), r) <= d_us:
                steal += 1
        # Penalize moves that would let opponent be much closer than us to the target
        val = d_us + 0.5 * d_op - 2.0 * (d_op - d_us) - 0.1 * steal
        if val < best_val - 1e-9:
            best_val = val
            best_move = [dx, dy]

    return best_move