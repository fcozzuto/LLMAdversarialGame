def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # If no visible resources, hold position unless we can safely increase distance.
    if not resources:
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = md(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Score moves by "competitive advantage" towards a resource,
    # with a small penalty for getting too close to opponent early.
    best_move = [0, 0]
    best_score = -10**18

    opp_d_now = md(sx, sy, ox, oy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate best resource target for us from this next position.
        our_best = -10**18
        for rx, ry in resources:
            d_ours = md(nx, ny, rx, ry)
            d_opp = md(ox, oy, rx, ry)
            # Positive means we are closer than opponent (good).
            adv = d_opp - d_ours
            # Prefer also reducing absolute distance to chosen target.
            target_v = adv * 10 - d_ours
            if target_v > our_best:
                our_best = target_v

        # Tactical: avoid stepping into likely opponent pressure region.
        opp_d_next = md(nx, ny, ox, oy)
        pressure = 0
        if opp_d_next <= 2:
            pressure = (3 - opp_d_next) * 8
        # Extra determinism nudge: prefer moves that reduce our nearest resource distance when tied.
        nearest = min(md(nx, ny, rx, ry) for rx, ry in resources)
        score = our_best - pressure - nearest * 0.1

        # If we currently are very far, encourage commitment by slightly favoring closer opponent too.
        if opp_d_now >= 5 and adv > 0:
            score += 1

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move