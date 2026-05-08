def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []

    selfset = set((int(p[0]), int(p[1])) for p in self_terr if len(p) >= 2)
    opposet = set((int(p[0]), int(p[1])) for p in opp_terr if len(p) >= 2)
    unq = set((int(p[0]), int(p[1])) for p in unclaimed if len(p) >= 2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    manh = lambda a, b, c, d: abs(a - c) + abs(b - d)

    # Pick target: expand to unclaimed adjacent to our territory; else grab unclaimed near opponent; else press opponent.
    frontier = []
    for (x, y) in unq:
        ok = False
        for dx, dy in dirs:
            if (x + dx, y + dy) in selfset:
                ok = True
                break
        if ok:
            frontier.append((x, y))

    if frontier:
        tx, ty = min(frontier, key=lambda p: (manh(p[0], p[1], ox, oy), p[0], p[1]))
    elif unq:
        tx, ty = min(unq, key=lambda p: (manh(p[0], p[1], ox, oy), p[0], p[1]))
    else:
        tx, ty = (ox, oy)

    # Obstacle-aware move scoring; prefer moving into opponent territory when they lead.
    opp_count = int(observation.get("opponent_territory_count", len(opposet)))
    self_count = int(observation.get("self_territory_count", len(selfset)))
    press = (opp_count >= self_count)

    best = (10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        dist_to_target = manh(nx, ny, tx, ty)
        into_opp = (nx, ny) in opposet
        into_us = (nx, ny) in selfset
        step_pen = 0 if (dx == 0 and dy == 0) else 0  # deterministic tie-break relies on ordering below
        # If pressing, being in opponent territory is valuable; otherwise treat it neutrally.
        opp_bonus = -3 if (press and into_opp) else (1 if into_opp else 0)
        # Mildly avoid drifting far from target when staying possible.
        score = dist_to_target + step_pen + opp_bonus
        if score < best[0] or (score == best[0] and (dx, dy) == (best[1], best[2])):
            best = (score, dx, dy)

    if best[0] == 10**9:
        return [0, 0]
    return [int(best[1]), int(best[2])]