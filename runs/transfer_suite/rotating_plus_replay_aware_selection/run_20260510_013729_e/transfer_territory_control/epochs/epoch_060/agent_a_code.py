def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    x, y = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best = None
    best_score = -10**9

    for dx, dy in candidates:
        nx, ny = x + dx, y + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        if resources:
            d = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
            score += 30 - 5 * d
        if unclaimed:
            d2 = min(abs(nx - ux) + abs(ny - uy) for ux, uy in unclaimed)
            score += 12 - 3 * d2
            if (nx, ny) in set(unclaimed):
                score += 20
        score += -2 * (abs(nx - ox) + abs(ny - oy))

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best