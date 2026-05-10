def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    selfT = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))
    opT = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opT.add((int(p[0]), int(p[1])))
    unT = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unT.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not unT:
        target_list = list(opT) if opT else [(sx, sy)]
    else:
        target_list = unT

    # nearest target from current position (fast heuristic)
    def d2(p, q):
        return (p[0] - q[0]) * (p[0] - q[0]) + (p[1] - q[1]) * (p[1] - q[1])

    # preselect a few closest targets to reduce computation
    closest = sorted(target_list, key=lambda t: d2((sx, sy), t))[:6] if target_list else [(sx, sy)]

    best = (-10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        in_self = cell in selfT
        in_op = cell in opT
        in_un = (not in_self) and (not in_op) and (cell in set(unT))  # exact if listed
        # If unclaimed list doesn't include cell, treat as small/unknown
        if not in_un and cell in set(unT):
            in_un = True

        # distance-to-frontier proxy: closer to any chosen target is better
        min_d = min((abs(nx - tx) + abs(ny - ty) for tx, ty in closest), default=0)

        # immediate gain approximation
        score = 0
        if in_un:
            score += 5
        if in_op:
            score += 4
        if in_self:
            score -= 1
        # avoid walls/obstacles by penalizing leaving grid already handled; add mild center bias off corners
        score -= min_d * 1.2
        # strong preference to push into opponent territory or unclaimed over staying still
        if dx == 0 and dy == 0:
            score -= 0.6

        # deterministic tie-break: prefer smaller (dx,dy) lexicographically
        key = (score, -dx, -dy)
        if (key[0], key[1], key[2]) > (best[0], best[1], best[2]):
            best = (key[0], dx, dy)

    return [int(best[1]), int(best[2])]