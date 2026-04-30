def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    def clamp(v, a, b):
        return a if v < a else b if v > b else v

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx + dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def score_pos(px, py):
        best = -10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = dist((px, py), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            # Prefer resources where we're at least as close as opponent; otherwise smaller value.
            # Lower distance to resource is better.
            lead = (do - ds)
            # Slightly bias away from being adjacent to opponent to reduce immediate contest.
            opp_prox = max(abs(px - ox), abs(py - oy))
            val = (lead * 3) - ds * 1.5 - (1.0 if opp_prox == 1 else 0.0)
            if val > best:
                best = val
        # If we stand on resource, be very strong.
        if any(px == rx and py == ry for rx, ry in resources):
            best += 1000
        return best

    best_move = [0, 0]
    best_score = -10**18
    # Deterministic tie-break order: prioritize moves that reduce dx,dy lexicographically.
    for dx, dy in sorted(moves, key=lambda m: (m[0], m[1])):
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        sc = score_pos(nx, ny)
        if sc > best_score:
            best_score = sc
            best_move = [dx, dy]
        elif sc == best_score:
            # Tie-break: prefer staying closer to opponent's direction of approach (keep a consistent bias).
            cur_t = (abs(sx - ox) + abs(sy - oy))
            nxt_t = (abs(nx - ox) + abs(ny - oy))
            if nxt_t < cur_t:
                best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]