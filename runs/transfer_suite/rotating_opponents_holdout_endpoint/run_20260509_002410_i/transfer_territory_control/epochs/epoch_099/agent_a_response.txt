def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    selfT = to_set("self_territory")
    oppT = to_set("opponent_territory")

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    targets = []
    for p in unclaimed:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                targets.append((x, y))

    if not targets:
        targets = [(ox, oy)]
    # target: closest unclaimed to opponent, tie-break by far from us
    tx, ty = min(targets, key=lambda t: (abs(t[0] - ox) + abs(t[1] - oy), -(abs(t[0] - sx) + abs(t[1] - sy))))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    best_score = -10**9

    cur_d = abs(sx - tx) + abs(sy - ty)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        if (nx, ny) in selfT:
            score = 8
        elif (nx, ny) in oppT:
            score = 5
        else:
            score = 10  # favors unclaimed/neutral

        nd = abs(nx - tx) + abs(ny - ty)
        score += (cur_d - nd) * 2  # move toward target
        score += (abs(nx - ox) + abs(ny - oy)) * -0.05  # slightly prefer closer to opponent

        # If moving into opponent, only if it's not a worse step than alternatives by much
        if (nx, ny) in oppT:
            score += 1 if nd <= cur_d else -1

        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]
        elif score == best_score:
            # deterministic tie-break: prefer smaller dx then smaller dy, then stay
            if (dx, dy) < (best[0], best[1]):
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return best