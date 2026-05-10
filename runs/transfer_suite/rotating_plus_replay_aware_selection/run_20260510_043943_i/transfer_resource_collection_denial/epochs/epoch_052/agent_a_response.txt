def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            nx, ny = sx, sy

        # Deterministic preference weights
        move_score = -10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)

            # Denier-aware: strongly prefer resources we can beat or that are "out of reach" soon
            beat = od - sd  # positive if we arrive sooner
            val = beat * 120 - sd * 2

            # If opponent arrives sooner, allow only when we're dramatically closer than they are
            if beat < 0:
                if sd <= od - 2:
                    val += 40  # still worth contesting
                else:
                    val -= (-(beat)) * 80

            # Small deterministic tie-breaker based on geometry
            val += ((rx * 3 + ry * 5 + sd + od) % 7) * 0.5

            if val > move_score:
                move_score = val

        # Prefer lexicographically smaller move on ties (deterministic)
        cand = move_score + (0.0001 * (dx + 2 * dy))
        if cand > best_score:
            best_score = cand
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]