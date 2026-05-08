def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = (observation.get("self_position") or [0, 0])[:2]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    ot = set(map(tuple, observation.get("opponent_territory") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a deterministic target: best frontier unclaimed cell adjacent to opponent territory; else nearest unclaimed; else center.
    target = None
    frontier = []
    for (x, y) in unclaimed:
        if ((x - 1, y) in ot) or ((x + 1, y) in ot) or ((x, y - 1) in ot) or ((x, y + 1) in ot) or \
           ((x - 1, y - 1) in ot) or ((x + 1, y - 1) in ot) or ((x - 1, y + 1) in ot) or ((x + 1, y + 1) in ot):
            frontier.append((x, y))
    if frontier:
        target = min(frontier, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), abs(p[0] - cx) + abs(p[1] - cy), p[0], p[1]))
    else:
        if unclaimed:
            target = min(unclaimed, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), abs(p[0] - cx) + abs(p[1] - cy), p[0], p[1]))
        else:
            target = (int(round(cx)), int(round(cy)))

    # Score each possible move by immediate cell value + distance-to-target reduction.
    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # immediate gain: opponent territory is valuable since flipping on entry is enabled.
        immediate = 0
        if (nx, ny) in ot:
            immediate += 1000
        elif (nx, ny) in unclaimed:
            immediate += 120
        # distance heuristic toward target
        dist_now = abs(sx - target[0]) + abs(sy - target[1])
        dist_next = abs(nx - target[0]) + abs(ny - target[1])
        val = immediate + (dist_now - dist_next) * 10 - (abs(nx - cx) + abs(ny - cy)) * 0.01
        # deterministic tie-break: smaller dx, then dy, then lexicographic target
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]