def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set(tuple(o) for o in (observation.get("obstacles") or []))
    opp_pos = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    unclaimed = observation.get("unclaimed_cells") or []

    if unclaimed:
        tx, ty = min(((int(x), int(y)) for x, y in unclaimed), key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    else:
        tx, ty = ox, oy

    center = (w // 2, h // 2)
    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        d_t = abs(nx - tx) + abs(ny - ty)
        score += -2.2 * d_t  # get to targets quickly

        if (nx, ny) in opp_terr:
            score += 12.0  # entering opponent territory flips control
        elif (nx, ny) in self_terr:
            score += 3.0  # consolidating

        # Reduce wasting moves by avoiding moving toward opponent's current position unless stealing
        d_opp_now = man((sx, sy), (ox, oy))
        d_opp_next = man((nx, ny), (ox, oy))
        score += 0.9 * (d_opp_now - d_opp_next)

        # Nudge toward center to avoid edge traps vs edge-claim opponent
        score += 0.25 * (man((sx, sy), center) - man((nx, ny), center))

        # Tiny deterministic tie-breaker
        score += -0.001 * (abs(dx) + abs(dy)) - 0.00001 * (nx + 31 * ny)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]