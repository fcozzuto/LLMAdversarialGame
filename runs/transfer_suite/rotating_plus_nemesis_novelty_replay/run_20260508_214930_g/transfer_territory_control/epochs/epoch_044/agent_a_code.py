def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Anchor targets: prefer unclaimed near us; if none, chase opponent territory edge.
    targets = list(unclaimed)
    if not targets:
        targets = list(opp_t)  # still try to pressure opponent area

    def dist(a, b):  # Manhattan
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Determine a simple "best direction" by scoring local move using global target proximity.
    if targets:
        # deterministic tie-break
        best_target = min(targets, key=lambda t: (dist((sx, sy), t), t[1], t[0]))
    else:
        best_target = (ox, oy)

    base_td = dist((sx, sy), best_target)
    base_odo = dist((sx, sy), (ox, oy))
    best = (0, 0)
    best_score = -10**18

    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue

        score = 0
        if (nx, ny) in opp_t:
            score += 900  # strong pressure via flipping
        if (nx, ny) in self_t:
            score += 8
        if (nx, ny) in unclaimed:
            score += 50

        # Move toward target unclaimed
        td = dist((nx, ny), best_target)
        score += (base_td - td) * 6

        # Keep some distance from opponent unless we are flipping
        odo = dist((nx, ny), (ox, oy))
        score += (odo - base_odo) * 2

        # Avoid dead patterns: prefer to expand from current territory/unclaimed edges
        # by counting how many favorable neighbor cells exist (deterministic local count).
        edge_bonus = 0
        for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            ax, ay = nx + adx, ny + ady
            if not (0 <= ax < w and 0 <= ay < h) or (ax, ay) in obstacles:
                continue
            if (ax, ay) in unclaimed:
                edge_bonus += 2
            if (ax, ay) in opp_t:
                edge_bonus += 3
        score += edge_bonus

        # Deterministic tie-break: prefer moves with larger (abs) progress toward target, then lexicographic dx,dy
        prog = base_td - dist((nx, ny), best_target)
        tieb = (prog, ddx, ddy)

        if score > best_score or (score == best_score and tieb > (base_td, best[0], best[1])):
            best_score = score
            best = (ddx, ddy)

    return [int(best[0]), int(best[1])]