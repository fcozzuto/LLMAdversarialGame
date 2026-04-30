def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target: if opponent is closer to a resource, deprioritize it.
    best = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Strongly prefer resources opponent can't reach quickly.
        score = (ds - do) * 5 + ds
        if best is None or score < best[0] or (score == best[0] and (rx, ry) < (best[1], best[2])):
            best = (score, rx, ry)
    tx, ty = (best[1], best[2]) if best else (sx, sy)

    # If at/near target, switch to the globally nearest resource.
    if resources and man(sx, sy, tx, ty) <= 1:
        near = None
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            if near is None or ds < near[0] or (ds == near[0] and (rx, ry) < (near[1], near[2])):
                near = (ds, rx, ry)
        tx, ty = near[1], near[2]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort()  # deterministic tie-break

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Greedy progress to target + mild opponent avoidance + obstacle adjacency penalty.
        d_to_t = man(nx, ny, tx, ty)
        d_to_o = man(nx, ny, ox, oy)
        opp_pen = -2 if d_to_o <= 2 else 0
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in obstacles:
                    adj_pen += 1
        val = d_to_t * 10 + adj_pen * 3 + opp_pen

        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]