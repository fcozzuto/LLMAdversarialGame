def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_in = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_in:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not inb(sx, sy) or w <= 0 or h <= 0:
        return [0, 0]

    if not resources:
        best = (0, 0, -10**18)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                score = -(abs(nx - ox) + abs(ny - oy))
                if score > best[2]:
                    best = (dx, dy, score)
        return [best[0], best[1]]

    # Deterministic preference: prefer middle resources first
    cx, cy = w // 2, h // 2
    targets = list(resources)
    targets.sort(key=lambda r: (abs(r[0] - cx) + abs(r[1] - cy), r[0], r[1]))

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # Evaluate each move: go toward nearest resource, but avoid squares the opponent reaches sooner
    best_dx, best_dy, best_score = 0, 0, -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_pos = (nx, ny)
        opp_pos = (ox, oy)

        # Find my closest and opponent closest resources
        my_best = 10**18
        opp_best = 10**18
        pick = None
        for r in targets:
            dr_my = dist2(my_pos, r)
            if dr_my < my_best:
                my_best = dr_my
                pick = r
        for r in targets:
            dr_opp = dist2(opp_pos, r)
            if dr_opp < opp_best:
                opp_best = dr_opp

        # Bonus if we can potentially grab a picked resource immediately
        immediate = 1 if pick is not None and (nx, ny) == (pick[0], pick[1]) else 0

        # If opponent is already very close to the same target, penalize
        opp_to_pick = dist2(opp_pos, pick) if pick is not None else 10**18
        score = -my_best
        score += 50 * immediate
        score -= 0.5 * opp_to_pick
        score -= 0.05 * (abs(nx - ox) + abs(ny - oy))

        if score > best_score:
            best_dx, best_dy, best_score = dx, dy, score

    return [best_dx, best_dy]