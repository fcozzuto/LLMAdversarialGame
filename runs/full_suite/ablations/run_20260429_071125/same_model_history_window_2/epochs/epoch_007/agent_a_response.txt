def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (None, -10**18)

    if not resources:
        # No resources: move to maximize distance from opponent (deterministic).
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            val = md(nx, ny, ox, oy)
            if val > best[1]:
                best = ((dx, dy), val)
        return [best[0][0], best[0][1]] if best[0] is not None else [0, 0]

    # Prioritize capturing/contesting; prefer moves that make us closer than opponent to at least one resource,
    # while also preventing opponent from getting an immediate capture next.
    topN = sorted(resources, key=lambda r: md(sx, sy, r[0], r[1]))[:6]
    opp_next_threat = []
    for r in topN:
        rx, ry = r[0], r[1]
        if md(ox, oy, rx, ry) == 1:
            opp_next_threat.append((rx, ry))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Main objective: maximize best lead across nearby resources.
        best_lead = -10**18
        capture_bonus = 0
        # Secondary: reduce opponent immediate capture chances (deterministic penalty).
        threat_pen = 0

        for rx, ry in topN:
            dS = md(nx, ny, rx, ry)
            dO = md(ox, oy, rx, ry)
            lead = dO - dS
            if dS == 0:
                capture_bonus = 1
                lead = 10**6
            if lead > best_lead:
                best_lead = lead

        for rx, ry in opp_next_threat:
            if md(nx, ny, rx, ry) > md(ox, oy, rx, ry):
                threat_pen += 1  # we let opponent be (or stay) the closer one

        val = best_lead * 100 + capture_bonus * 1000 - threat_pen * 50
        if val > best[1]:
            best = ((dx, dy), val)

    return [best[0][0], best[0][1]] if best[0] is not None else [0, 0]