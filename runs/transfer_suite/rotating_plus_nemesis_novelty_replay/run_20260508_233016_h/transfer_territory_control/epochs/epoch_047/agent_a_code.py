def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    cx, cy = w // 2, h // 2
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Prefer immediate flipping of opponent territory on entry
    adjacent_flip = None
    best_flip_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in opp_terr:
            sc = 1000 - dist((nx, ny), (sx, sy))  # deterministic
            if sc > best_flip_score:
                best_flip_score = sc
                adjacent_flip = (dx, dy)
    if adjacent_flip is not None:
        return [adjacent_flip[0], adjacent_flip[1]]

    # Target selection: claim closer-to-center unclaimed; if none, push toward opponent or center.
    unclaimed_list = [c for c in unclaimed if c not in obstacles]
    if unclaimed_list:
        # deterministic: sort key by (center-dist, self-dist, x, y)
        target = sorted(unclaimed_list, key=lambda c: (dist(c, (cx, cy)), dist(c, (sx, sy)), c[0], c[1]))[0]
    else:
        opp_list = [c for c in opp_terr if c not in obstacles]
        if opp_list:
            target = sorted(opp_list, key=lambda c: (dist(c, (sx, sy)), abs(c[0] - cx) + abs(c[1] - cy), c[0], c[1]))[0]
        else:
            target = (cx, cy)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            # invalid moves get rejected by engine; avoid choosing them
            continue
        cell = (nx, ny)

        val = 0.0
        if cell in unclaimed:
            val += 5.0
        if cell in self_terr:
            val += 0.6
        if cell in opp_terr:
            val += 6.0  # should have been caught, but keep consistent
        # "territory control" favors progressing toward target
        val += -0.9 * dist(cell, target)

        # Mild preference to reduce distance to center once close
        val += -0.05 * dist(cell, (cx, cy))

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]