def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells") or []
    my_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    their_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    candidates = unclaimed
    if not candidates:
        candidates = list(their_terr)

    # Aim: counterclaim by stepping into opponent territory when possible; otherwise race to nearest unclaimed.
    # Also discourage moving away from the opponent when ahead is unlikely.
    tx, ty = ox, oy
    if candidates:
        # Deterministic: pick nearest unclaimed cell to opponent, tie-break by closeness to us.
        tx, ty = min(candidates, key=lambda c: (abs(c[0] - ox) + abs(c[1] - oy), abs(c[0] - sx) + abs(c[1] - sy), c[0], c[1]))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        dist_to_target = abs(nx - tx) + abs(ny - ty)
        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        dist_from_opp = abs(nx - ox) + abs(ny - oy)

        # Strong preference for capturing: if move enters opponent territory.
        enters_theirs = (nx, ny) in their_terr
        enters_unclaimed = (nx, ny) in my_terr
        # Score key: maximize capture chance and progress to target, while avoiding self traps.
        # Deterring "stalling" unless it's best.
        key = (
            0 if enters_theirs else 1,
            dist_to_target,
            -dist_from_opp,  # prefer being closer to opponent (counterclaim style)
            0 if (nx, ny) in my_terr else 1,  # prefer not to leave own territory unless it progresses
            abs(dx) + abs(dy),
            nx, ny
        )

        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    # If no legal move found (surrounded by obstacles), stay.
    return [int(best_move[0]), int(best_move[1])]