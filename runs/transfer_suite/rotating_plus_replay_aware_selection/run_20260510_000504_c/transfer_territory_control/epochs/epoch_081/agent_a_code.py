def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    resources = observation.get("resources") or []

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def neigh_count(adjset, x, y):
        c = 0
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if (nx, ny) in adjset:
                c += 1
        return c

    def best_target_step(tx, ty):
        best = (10**9, [0, 0])
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = abs(tx - nx) + abs(ty - ny)
            if d < best[0]:
                best = (d, [dx, dy])
        return best[1]

    # If we see a resource, take a deterministic step toward it (materially different from prior simplistic expansion).
    if resources:
        tx, ty = resources[0]
        return best_target_step(tx, ty)

    # Otherwise: evaluate one-step moves by estimated immediate control and "safer" positioning.
    best_score = -10**9
    best_move = [0, 0]
    opp_cells = list(opp_terr)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Immediate control gain: unclaimed or opponent territory we would flip into our control.
        if (nx, ny) in self_terr:
            gain = 0.0
        elif (nx, ny) in opp_terr:
            gain = 1.2
        elif (nx, ny) in unclaimed:
            gain = 1.0
        else:
            gain = 0.0

        # Prefer moves that extend our frontier (adjacent to our territory).
        frontier = neigh_count(self_terr, nx, ny)

        # Prefer being farther from opponent territory to avoid being swept back.
        if opp_cells:
            mind = 10**9
            for ox, oy in opp_cells:
                dd = abs(ox - nx) + abs(oy - ny)
                if dd < mind:
                    mind = dd
        else:
            mind = 99
        safety = 0.06 * mind

        # Slight preference for moving (avoid stalling unless forced).
        move_pen = 0.03 * (0 if (dx == 0 and dy == 0) else 1)

        score = gain + 0.45 * frontier + safety - move_pen

        # Deterministic tie-break: lexicographic (dx, dy).
        cand_move = [dx, dy]
        if score > best_score or (score == best_score and cand_move < best_move):
            best_score = score
            best_move = cand_move

    return best_move