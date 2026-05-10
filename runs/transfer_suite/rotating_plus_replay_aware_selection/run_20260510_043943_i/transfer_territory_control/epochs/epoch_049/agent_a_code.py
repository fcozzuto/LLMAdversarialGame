def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = set()
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                resources.add((x, y))

    opp_t = set()
    for p in observation.get("opponent_territory", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_t.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))
    if not unclaimed:
        unclaimed = [(x, y) for x in range(w) for y in range(h) if (x, y) not in obstacles and (x, y) not in opp_t]

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        ds = abs(nx - sx) + abs(ny - sy)
        # (ds is always 1; keep structure simple and deterministic)
        cur_self_dist = abs(nx - ox) + abs(ny - oy)

        # Target evaluation: closest "worthwhile" cell based on resource and territorial pressure.
        local_best = -10**18
        for tx, ty in unclaimed[:30]:
            self_d = abs(tx - nx) + abs(ty - ny)
            opp_d = abs(tx - ox) + abs(ty - oy)
            val = (opp_d - self_d)  # prefer cells we can reach sooner
            if (tx, ty) in resources:
                val += 5
            if (tx, ty) in opp_t:
                val -= 2
            local_best = val if val > local_best else local_best

        # Also reward moving closer to the opponent to force cuts against them (deterministic pressure).
        score = local_best + (2 if (nx, ny) in resources else 0) - (cur_self_dist // 10)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]