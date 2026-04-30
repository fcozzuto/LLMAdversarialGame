def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    resset = set(resources)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def d2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    if not resources:
        best = None
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            v = d2(nx, ny, ox, oy)
            if best is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    # Opponent's likely target: closest remaining resource to opponent.
    opp_target = min(resources, key=lambda r: d2(ox, oy, r[0], r[1]))
    otx, oty = opp_target

    best_move = (0, 0)
    best_val = -10**30

    # Blocking/contesting: get close to opponent's target while still advancing to resources.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        val = 0
        if (nx, ny) in resset:
            val += 10**9

        # Make ourselves a strong contender at opponent's target.
        val += 4000 - d2(nx, ny, otx, oty)

        # Also keep ourselves moving toward any remaining resource (not just theirs).
        val += 800 - min(d2(nx, ny, rx, ry) for (rx, ry) in resources)

        # Mildly discourage giving opponent a clear grab by staying away from them unless contesting.
        val += 50 - d2(nx, ny, ox, oy)

        # Deterministic tie-break: lexicographic by move order.
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]