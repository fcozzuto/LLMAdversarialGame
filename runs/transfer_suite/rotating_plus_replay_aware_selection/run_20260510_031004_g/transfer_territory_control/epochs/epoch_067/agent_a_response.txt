def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))
    unclaimed = observation.get("unclaimed_cells", []) or []

    candidates = []
    for p in unclaimed:
        t = tuple(p)
        if ok(t[0], t[1]):
            candidates.append((t, 1.0))
    for p in opp_terr:
        if ok(p[0], p[1]):
            candidates.append((tuple(p), 2.5))
    if not candidates:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -1e18

    # Deterministic tie-break: fixed candidate order + fixed move iteration.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Immediate landing value
        tset = (nx, ny)
        if tset in opp_terr:
            land = 3.0
        elif tset in self_terr:
            land = -0.1
        else:
            land = 1.2 if tset in set(map(tuple, unclaimed)) else 0.2

        # Look toward the most favorable reachable target
        best_t = None
        best_key = None
        for (tx, ty), b in candidates:
            # Prefer close to us, far from opponent; slight bias to center for stability
            d1 = abs(tx - nx) + abs(ty - ny)
            d2 = abs(tx - ox) + abs(ty - oy)
            center = abs((tx - (w - 1) / 2.0)) + abs((ty - (h - 1) / 2.0))
            key = (d1 - 0.35 * d2 + 0.02 * center, d1, -b)
            if best_key is None or key < best_key:
                best_key = key
                best_t = (tx, ty, b)

        tx, ty, b = best_t
        d1 = best_key[0]  # already contains combined; but we can approximate using abs
        direct = abs(tx - nx) + abs(ty - ny)
        # Prefer targets that we can reach sooner than opponent
        winpush = (abs(tx - ox) + abs(ty - oy)) - direct

        score = land + 1.4 * b - 0.12 * direct + 0.18 * winpush
        # Small phase-based bias to avoid symmetric loops
        if (observation.get("turn_index", 0) % 2) == 1 and (nx + ny) % 2 == 0:
            score += 0.03

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]