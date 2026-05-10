def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    # Prefer unclaimed cells adjacent to our territory (frontier claim)
    targets = []
    for (x, y) in self_t:
        for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) in unclaimed:
                targets.append((nx, ny))
    if not targets:
        targets = list(unclaimed)

    if not targets:
        # If no unclaimed, expand into opponent territory if possible; else hold/approach center
        targets = list(opp_t) if opp_t else []

    nbrs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = (0, 0)
    best_key = None

    # Local scoring of candidate moves
    for dx, dy in nbrs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in obstacles:
            continue

        # Determine cell category
        in_unclaimed = (nx, ny) in unclaimed
        in_opp = (nx, ny) in opp_t
        in_self = (nx, ny) in self_t

        # Distance to best target
        if targets:
            d_to_target = min(manh((nx, ny), t) for t in targets)
            d_to_opp = man((nx, ny), (ox, oy))
        else:
            d_to_target = 0
            d_to_opp = man((nx, ny), (ox, oy))

        # Prefer claiming unclaimed; otherwise attack opponent territory.
        # Tie-break: approach target, and also prefer staying away from immediate opponent if it helps survival.
        if in_unclaimed:
            cat = 0
        elif in_opp:
            cat = 1
        elif in_self:
            cat = 2
        else:
            cat = 3

        # Avoid giving opponent an easy recapture: if stepping onto our own area, prefer not adjacent to opponent.
        adj_to_opp = max(abs(nx - ox), abs(ny - oy)) <= 1

        # Earlier turns are more aggressive; later turns more defensive.
        t_idx = int(observation.get("turn_index", 0) or 0)
        aggressive = 0.35 if t_idx < 40 else 0.2

        # Key: lower is better
        key = (
            cat,
            d_to_target,
            int(adj_to_opp and in_self and not in_unclaimed),
            int(d_to_opp == 0),
            -int(in_opp) * (1 + aggressive),
        )

        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]