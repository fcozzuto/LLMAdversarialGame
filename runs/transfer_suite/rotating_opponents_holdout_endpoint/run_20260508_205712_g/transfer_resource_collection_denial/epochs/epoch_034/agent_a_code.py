def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    res_set = set((r[0], r[1]) for r in resources)

    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # If no resources visible, head to center (deterministic).
    if not resources:
        tx, ty = (W - 1) // 2, (H - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Score moves: immediate pickup + relative access to resources vs opponent.
    best_score = -(10**30)
    best_move = (0, 0)
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in res_set:
            score += 10**9

        # Focus on nearest resources to reduce computation and improve reactivity.
        # Deterministic: iterate resources sorted by (distance, x, y) from current position.
        ordered = sorted(resources, key=lambda r: (man(sx, sy, r[0], r[1]), r[0], r[1]))
        for k, (rx, ry) in enumerate(ordered[:6]):
            d_self = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            # Encourage moves that make us closer than opponent; strongly reward "next turn" access.
            rel = d_opp - d_self
            score += (rel * 2000) - (d_self * 35) - (k * 3)
            if d_self == 0:
                score += 500000
            elif d_self == 1:
                score += 70000

        # Small preference for moving toward any resource to avoid stalling.
        # Tie-break deterministically by favoring smaller dx/dy lexicographically.
        score += -man(nx, ny, ordered[0][0], ordered[0][1]) * 5

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]