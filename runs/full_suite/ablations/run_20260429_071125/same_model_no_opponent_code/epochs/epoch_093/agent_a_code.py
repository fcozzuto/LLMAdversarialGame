def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        candidates = [(dx, dy) for dx, dy in deltas if valid(sx + dx, sy + dy)]
        candidates.sort()
        best = None
        bestv = -10**18
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - ox) + abs(ny - oy)
            v = d
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best if best is not None else [0, 0]

    best_target = None
    best_d = 10**18
    for rx, ry in resources:
        d = abs(rx - sx) + abs(ry - sy)
        if d < best_d or (d == best_d and (rx, ry) < best_target):
            best_d = d
            best_target = (rx, ry)

    rx, ry = best_target
    candidates = [(dx, dy) for dx, dy in deltas if valid(sx + dx, sy + dy)]
    candidates.sort()

    best = None
    best_score = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        dist_to_res = abs(rx - nx) + abs(ry - ny)
        dist_to_opp = abs(ox - nx) + abs(oy - ny)
        score = -dist_to_res + 0.05 * dist_to_opp
        if score > best_score:
            best_score = score
            best = [dx, dy]
    return best if best is not None else [0, 0]