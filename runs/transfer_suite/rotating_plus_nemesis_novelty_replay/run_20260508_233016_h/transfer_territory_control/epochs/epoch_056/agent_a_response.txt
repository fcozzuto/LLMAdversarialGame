def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    un = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) // 2, (h - 1) // 2
    center = (cx, cy)

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = [0, 0]
    best_score = -10**18
    t = observation.get("turn_index", 0)

    # Bias changes across game to avoid repeating a weak policy.
    # Deterministic: alternate between "invade" and "consolidate".
    invade_mode = (t % 10) < 5

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        in_self = (nx, ny) in selfT
        in_opp = (nx, ny) in oppT
        in_un = (nx, ny) in un

        # Territory capture value (flipping on entry is enabled).
        if in_opp:
            gain = 9
        elif in_un:
            gain = 4
        elif in_self:
            gain = 1
        else:
            # rare: should mostly be adjacent to unclaimed; treat as neutral
            gain = 2

        # Prefer frontier pressure when invading; otherwise prefer center control and safety.
        d_opp = man(nx, ny, ox, oy)
        d_ctr = man(nx, ny, center[0], center[1])

        # If we can move into opponent, strongly reward closing distance; otherwise keep a small buffer.
        if invade_mode or in_opp:
            pursuit = (9 - min(d_opp, 9)) * 2
        else:
            pursuit = (min(d_opp, 9)) * 1

        # Encourage shaping toward center and away from wasting moves.
        shape = (18 - min(d_ctr, 18)) * (2 if not in_opp else 1)

        # Small reward for reducing local openness: target cells adjacent to our territory.
        adj_self = 0
        for ax, ay in candidates:
            px, py = nx + ax, ny + ay
            if (px, py) in selfT:
                adj_self += 1
        adj_bonus = adj_self * 1.5

        score = gain * 100 + pursuit * 10 + shape * 3 + adj_bonus

        # Slight deterministic tie-breaker to reduce dithering.
        tie = (dx, dy) == (0, 0)
        if score > best_score or (score == best_score and (tie, dx, dy) < (best_score, best[0], best[1])):
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]