def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    self_terr = set(tuple(t) for t in (observation.get("self_territory") or []))
    opp_terr = set(tuple(t) for t in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(t) for t in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)

    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(ox), int(oy)

    myc = int(observation.get("self_territory_count") or 0)
    oppc = int(observation.get("opponent_territory_count") or 0)
    behind = myc < oppc

    targets = observation.get("unclaimed_cells") or []
    if not targets or not behind:
        targets = list(opp_terr) if opp_terr else list(unclaimed)
    if not targets:
        targets = [(ox, oy), (w - 1, h - 1), (0, 0)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # pick one deterministic strategic target
    tbest = None
    for t in targets:
        tx, ty = int(t[0]), int(t[1])
        score = dist((sx, sy), (tx, ty)) + (0 if behind else 2 * dist((ox, oy), (tx, ty)))
        if tbest is None or score < tbest[0] or (score == tbest[0] and (ty, tx) < (tbest[1][1], tbest[1][0])):
            tbest = (score, (tx, ty))
    tx, ty = tbest[1]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) in opp_terr:
            gain = 5
        elif (nx, ny) in unclaimed:
            gain = 3
        elif (nx, ny) in self_terr:
            gain = 1
        else:
            gain = 0
        # prefer decreasing distance to target; slight preference to approach opponent when not behind
        d = dist((nx, ny), (tx, ty))
        approach = -dist((nx, ny), (ox, oy)) if not behind else 0
        tie = ((observation.get("turn_index") or 0) + (dx + 2) * 7 + (dy + 2) * 13) % 3
        val = gain * 100 - d + approach + tie * 0.001
        candidates.append((val, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda x: (x[0], -x[2], x[1]))
    _, dx, dy = candidates[-1]
    return [int(dx), int(dy)]