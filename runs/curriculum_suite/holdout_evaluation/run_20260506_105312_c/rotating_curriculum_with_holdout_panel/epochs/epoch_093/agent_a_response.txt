def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                targets.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if (not inb(sx, sy)) or (sx, sy) in obs:
        sx, sy = 0, 0

    # If no resources are visible, just drift away from opponent while staying safe.
    if not targets:
        best = (0, 0)
        bestd = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = abs(nx - ox) + abs(ny - oy)
            if d > bestd or (d == bestd and (dx, dy) < best):
                bestd, best = d, (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_score = -10**18
    best_tiebreak = None

    # Interceptor/denier: pick move maximizing advantage on the closest "contested" resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        my_best = 10**9
        opp_best = 10**9
        advantage = -10**9
        for tx, ty in targets:
            md = abs(nx - tx) + abs(ny - ty)
            od = abs(ox - tx) + abs(oy - ty)
            # Favor resources I can reach sooner; penalize where opponent is closer.
            # Small "tie" bias toward immediate closeness.
            adv = (od - md) * 10 - md
            if md < my_best:
                my_best = md
            if od < opp_best:
                opp_best = od
            if adv > advantage:
                advantage = adv

        # Secondary: avoid stepping into opponent's immediate neighborhood.
        opp_near = 0
        for ddx, ddy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            if (nx + ddx, ny + ddy) == (ox, oy):
                opp_near = 1
                break

        score = advantage - opp_near * 50
        tiebreak = (my_best, opp_best, dx, dy)

        if score > best_score or (score == best_score and (best_tiebreak is None or tiebreak < best_tiebreak)):
            best_score = score
            best_move = (dx, dy)
            best_tiebreak = tiebreak

    return [int(best_move[0]), int(best_move[1])]