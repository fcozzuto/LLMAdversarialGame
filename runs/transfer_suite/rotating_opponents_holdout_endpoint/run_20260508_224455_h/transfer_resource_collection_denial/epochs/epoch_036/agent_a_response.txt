def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    res_set = set((p[0], p[1]) for p in resources)

    def man(a, b, c, d):
        dx = a - c
        dy = b - d
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            candidates.append((dx, dy))

    if not candidates:
        return [0, 0]

    best_move = None
    best_val = None

    # Denier-aware: prefer resources where we're closer and opponent is not.
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in res_set:
            val = 10_000  # immediate collection
        else:
            # Compute best achievable "advantage" among remaining resources from this next cell.
            # Tie-break deterministically by (self closer first, then higher advantage, then dx/dy order).
            val = -10**9
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                ds = man(nx, ny, rx, ry)
                do = man(ox, oy, rx, ry)
                # Resource priority:
                # - If opponent is closer, heavily penalize.
                # - Otherwise prefer larger advantage and closer absolute distance.
                if do <= ds:
                    cur = -2_000_000 + (do - ds)  # discourage deniable targets
                else:
                    cur = (do - ds) * 100 - ds
                if cur > val:
                    val = cur

        key = (-(val), abs(dx) + abs(dy), dx, dy)
        if best_val is None or key < best_move:
            best_val = val
            best_move = key
            best = [dx, dy]

    return best