def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) // 2, (h - 1) // 2
    targets = list(unclaimed)
    if not targets:
        targets = [(cx, cy), (cx - 1, cy), (cx, cy - 1), (cx + 1, cy), (cx, cy + 1)]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best = None
    best_val = -10**18

    # Prefer a target that is reachable without stepping into obstacles in first move.
    # Score uses local approximation: claim/flip > approach unclaimed.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0
        if (nx, ny) in opp_terr:
            val += 500  # entering opponent territory flips control
        elif (nx, ny) in unclaimed:
            val += 50  # claiming new territory
        elif (nx, ny) in self_terr:
            val += 10  # maintaining control

        # Approach a good unclaimed target; otherwise approach center.
        tbest = None
        tdist = None
        for tx, ty in targets:
            if not (0 <= tx < w and 0 <= ty < h):
                continue
            d = abs(nx - tx) + abs(ny - ty)
            if tdist is None or d < tdist or (d == tdist and (tx, ty) < tbest):
                tdist, tbest = d, (tx, ty)
        if tdist is None:
            tdist = abs(nx - cx) + abs(ny - cy)
        val += -3 * tdist

        # Keep some pressure: if close to opponent, move to interact; otherwise avoid being pinned.
        dop = abs(nx - ox) + abs(ny - oy)
        val += (10 if dop <= 2 else 0) - 1.5 * dop

        # Small tie-breaker: deterministic order by dx,dy preference (center-ish first)
        tb = - (abs(dx) + abs(dy))  # prefer staying/moving lightly when equal
        val += 0.001 * tb

        if best is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]