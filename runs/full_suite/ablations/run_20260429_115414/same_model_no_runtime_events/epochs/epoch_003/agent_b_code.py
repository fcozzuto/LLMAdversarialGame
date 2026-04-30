def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def safe(x, y):
        return inb(x, y) and (x, y) not in obstacles

    # Pick a small deterministic set of promising resources (closest to either agent).
    scored = []
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        s = dist((sx, sy), (rx, ry))
        o = dist((ox, oy), (rx, ry))
        scored.append((min(s, o), s, o, rx, ry))
    if not scored:
        return [0, 0]
    scored.sort(key=lambda t: (t[0], t[1], t[2], t[3], t[4]))
    candidates = scored[:5]  # keep cheap and strategic

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        # One-step lookahead: prefer moves that make us closer than opponent to top candidate resources.
        val = 0
        tie = 0
        for _, scur, ocur, rx, ry in candidates:
            sn = dist((nx, ny), (rx, ry))
            # If we can get ahead on distance, score heavily; otherwise still move toward.
            lead = ocur - sn
            val += lead * 20 + (ocur - scur)  # deterministic mixture
            tie += (rx * 37 + ry * 17 + sn)  # deterministic tie component
        # Mild obstacle avoidance: discourage moves that would step next to an obstacle too directly.
        adj = 0
        for ax, ay in [(nx - 1, ny), (nx + 1, ny), (nx, ny - 1), (nx, ny + 1)]:
            if inb(ax, ay) and (ax, ay) in obstacles:
                adj += 1
        val -= adj * 2
        # Deterministic tie-break favoring moves that keep us more central relative to board.
        center_bias = - (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
        val += center_bias * 0.001
        key = (val, -tie, dx, dy)
        if best_val is None or key > best_val:
            best_val = key
            best_move = (dx, dy)

    # If all moves invalid (shouldn't happen), stay.
    return [int(best_move[0]), int(best_move[1])]