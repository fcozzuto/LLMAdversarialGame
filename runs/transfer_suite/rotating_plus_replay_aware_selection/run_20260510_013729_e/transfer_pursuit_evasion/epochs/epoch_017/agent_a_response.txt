def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    ob = []
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            ob.append((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    pursuer = "pursuer" in role

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if any(nx == px and ny == py for px, py in ob):
            continue

        d = abs(nx - ox) + abs(ny - oy)
        edge = min(nx, w - 1 - nx, ny, h - 1 - ny)
        if ob:
            obst_d = min(abs(nx - px) + abs(ny - py) for px, py in ob)
        else:
            obst_d = 99

        # Higher is better for pursuer and lower is better for evader
        # Keep clear from obstacles, but allow if it helps closing/opening distance.
        if pursuer:
            val = (-d * 10) + (edge * 0.3) + (obst_d * 0.8)
            # Prefer immediate "better than stay"
            if dx == 0 and dy == 0:
                val -= 0.5
        else:
            val = (d * 10) + (edge * 0.1) + (obst_d * 0.6)
            if dx == 0 and dy == 0:
                val -= 0.2

        cand.append((val, nx, ny, dx, dy))

    if not cand:
        return [0, 0]

    # Deterministic tie-breaker: lexicographic by position then move
    cand.sort(key=lambda t: (-t[0], t[1], t[2], t[3], t[4]))
    return [int(cand[0][3]), int(cand[0][4])]