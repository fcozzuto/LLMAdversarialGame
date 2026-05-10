def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    pref = {(-1, 0): 0, (1, 0): 1, (0, -1): 2, (0, 1): 3, (-1, -1): 4, (1, -1): 5, (-1, 1): 6, (1, 1): 7, (0, 0): 8}

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        # Expand toward map center while avoiding obstacles
        tx, ty = w // 2, h // 2
        best = (-(10**9), 0)
        bestm = [0, 0]
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            selfd = abs(nx - tx) + abs(ny - ty)
            score = -selfd
            if score > best[0] or (score == best[0] and pref[(dx, dy)] < best[1]):
                best = (score, pref[(dx, dy)])
                bestm = [dx, dy]
        return bestm

    best = None
    bestm = [0, 0]

    # Score a candidate by best achievable advantage over opponent on remaining resources
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        # If we step onto a resource, it's usually optimal
        self_best = 10**9
        opp_best = 10**9
        self_to_resource_on_move = 0
        for rx, ry in resources:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            if sd == 0:
                self_to_resource_on_move = 1
            if sd < self_best:
                self_best = sd
                opp_best = od
            elif sd == self_best and od < opp_best:
                opp_best = od
        # Advantage favors smaller self distance relative to opponent
        advantage = opp_best - self_best
        # Tie-break: prefer immediate collection, then smaller self_best, then deterministic move order
        score_tuple = (self_to_resource_on_move, advantage, -self_best, -abs((nx + ny) - (ox + oy)))
        if best is None or score_tuple > best or (score_tuple == best and pref[(dx, dy)] < pref[tuple(bestm)]):
            best = score_tuple
            bestm = [dx, dy]

    return bestm