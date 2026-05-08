def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles if len(p) >= 2)
    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []

    selfset = set((int(p[0]), int(p[1])) for p in self_terr if len(p) >= 2)
    opposet = set((int(p[0]), int(p[1])) for p in opp_terr if len(p) >= 2)
    unq = set((int(p[0]), int(p[1])) for p in unclaimed if len(p) >= 2)

    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose a deterministic target: prefer nearby unclaimed; otherwise attack nearest opponent territory.
    if unq:
        # Prefer "frontier-ish" unclaimed closer to opponent; frontier approximated by distance to opponent.
        target = min(unq, key=lambda p: (manh(p[0], p[1], ox, oy), p[0], p[1]))
    elif opposet:
        target = min(opposet, key=lambda p: (manh(p[0], p[1], ox, oy), p[0], p[1]))
    else:
        target = (w // 2, h // 2)

    # Evaluate moves
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        gain = 0
        if (nx, ny) in unq:
            gain += 6
        if (nx, ny) in selfset:
            gain += 1
        if (nx, ny) in opposet:
            gain += 4  # flipping on entry
        # Move quality: get closer to target, also nudge away from own inertia if target is elsewhere
        dist_to_target = manh(nx, ny, target[0], target[1])
        dist_to_opp = manh(nx, ny, ox, oy)
        # Prefer reducing distance to opponent when attacking; otherwise still keep moving toward target.
        proximity_bonus = -dist_to_target * 2 + (-dist_to_opp if unq or opposet else 0) * 0.3
        score = gain + proximity_bonus
        key = (-score, dx, dy, nx, ny)  # deterministic tie-break
        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]