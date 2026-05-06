def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        return [dx, dy]

    best_val = -10**18
    best = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        my_dists = []
        opp_dists = []
        for rx, ry in resources:
            r = (rx, ry)
            my_dists.append(manh((nx, ny), r))
            opp_dists.append(manh((ox, oy), r))

        my_best = min(my_dists)
        opp_best = min(opp_dists)

        best_delta = -10**18
        for i in range(len(resources)):
            d_m = my_dists[i]
            d_o = opp_dists[i]
            delta = d_o - d_m  # positive means I'm closer than opponent
            if delta > best_delta:
                best_delta = delta

        risk = 0
        if (nx, ny) == (ox, oy):
            risk = -50
        # Prefer moves that create a clear lead on at least one resource and reduce opponent best access
        val = (best_delta * 35) + ((opp_best - my_best) * 18) - (my_best * 2) + risk
        if val > best_val:
            best_val = val
            best = [dx, dy]

    return best