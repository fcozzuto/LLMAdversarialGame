def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    center = ((w - 1) // 2, (h - 1) // 2)

    # Deterministic tie-break order: fixed dir list order, then score.
    best_move = [0, 0]
    best_val = -10**18

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a primary target (nearest unclaimed; else center; else any neighbor)
    if unclaimed:
        tx, ty = min(unclaimed, key=lambda p: (manh((sx, sy), p), p[0], p[1]))
    else:
        tx, ty = center

    # If opponent territory is nearby, prefer counterclaiming it when reachable.
    # Use a small lookahead based on distance to nearest opponent-territory cell.
    if opp_terr:
        od = min(manh((sx, sy), p) for p in opp_terr)
    else:
        od = 999

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        if cell in opp_terr:
            val = 1000
            val += -manh(cell, (tx, ty)) * 0.1
            # Strongly encourage taking when close to opponent influence.
            val += (10 - od) * 5 if od <= 3 else 0
        elif cell in unclaimed:
            val = 200
            val += -manh(cell, (tx, ty))
            val += (1 if nx == tx or ny == ty else 0)
        elif cell in self_terr:
            val = 20
            # Stay moving toward target, avoid getting stuck.
            val += -manh(cell, (tx, ty)) * 0.5
        else:
            val = 5
            val += -manh(cell, (tx, ty)) * 0.2

        # Mild preference for staying within central lanes early; deterministic.
        val += -0.01 * manh(cell, center)

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move