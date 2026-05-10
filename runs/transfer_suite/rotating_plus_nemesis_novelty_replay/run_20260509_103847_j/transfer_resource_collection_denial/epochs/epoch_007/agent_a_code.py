def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp = (ox, oy)

    # Pick a resource we can contest (self arrival <= opponent arrival). If none, pick closest-to-beat anyway.
    best = None
    for r in resources:
        sd = dist((sx, sy), r)
        od = dist(opp, r)
        slack = od - sd
        # Prefer: positive slack; then larger slack; then nearer self; then deterministic coord.
        if sd <= od:
            key = (0, -slack, sd, r[0], r[1])
        else:
            # Still race: minimize opponent advantage, then self distance
            key = (1, slack, sd, r[0], r[1])
        if best is None or key < best[0]:
            best = (key, r)
    tx, ty = best[1]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Slight obstacle-aware penalty by counting blocked neighbors around the candidate.
    dirs = moves
    def blocked_neighbors(x, y):
        cnt = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                cnt += 1
        return cnt

    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ns = dist((nx, ny), (tx, ty))
        no = dist(opp, (tx, ty))
        adv = no - ns  # larger is better: we arrive earlier than opponent
        # Add a small "shadow" avoidance: don't chase opponent into tight areas.
        to_opp = dist((nx, ny), opp)
        opp_adv = -to_opp
        key = (-adv, ns, blocked_neighbors(nx, ny), -opp_adv, dx, dy)
        if bestm is None or key < bestm[0]:
            bestm = (key, (dx, dy))

    return list(bestm[1]) if bestm is not None else [0, 0]