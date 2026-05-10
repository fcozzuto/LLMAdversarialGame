def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Prefer targets on opponent edge: unclaimed cells adjacent to opponent territory.
    opp_edge = []
    for (x, y) in oppT:
        for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)):
            nx, ny = x + dx, y + dy
            if ok(nx, ny) and (nx, ny) in unclaimed and (nx, ny) not in selfT:
                # tie-breaker: closer to our position, then smaller coords
                opp_edge.append((nx, ny))
    targets = opp_edge

    # If no edge cells visible, go toward nearest unclaimed.
    if not targets:
        if unclaimed:
            targets = list(unclaimed)
        else:
            targets = list(oppT) if oppT else [(ox, oy)]

    # Score candidate target by distance from our position and away from obstacles via greedy neighbor check.
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cand_move = None
    bestv = -10**18

    # Evaluate immediate moves: prefer move that reduces distance to target frontier and avoids moving into opponent territory too early.
    # (Edge-claimer opponent tends to expand; we counter-advance onto their boundary.)
    # Determine a single best target deterministically.
    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
    best_target = None
    for t in targets:
        if not ok(t[0], t[1]):
            continue
        v = dist((sx, sy), t) * 10 + dist((ox, oy), t)
        if best_target is None or v < bestv:
            best_target, bestv = t, v

    tx, ty = (best_target if best_target is not None else (ox, oy))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Desired: closer to frontier; if stepping into opponent territory, still allowed, but slightly penalize unless it helps reach target.
        step_to_target = dist((nx, ny), (tx, ty))
        step_from_self = dist((sx, sy), (tx, ty))
        into_opp = 1 if (nx, ny) in oppT else 0
        into_self = 1 if (nx, ny) in selfT else 0
        # Encourage exploring unclaimed; if move lands on unclaimed, give boost.
        on_unclaimed = 1 if (nx, ny) in unclaimed else 0
        v = -step_to_target * 3 + (step_from_self - step_to_target) * 5 + on_unclaimed * 8 - into_opp * 2 + into_self * 1
        # Tiny deterministic tie-breaker
        v += -(nx * 17 + ny)
        if cand_move is None or v > bestv:
            bestv = v
            cand_move = [dx, dy]

    if cand_move is None:
        return [0, 0]
    return [int(cand_move[0]), int(cand_move[1])]