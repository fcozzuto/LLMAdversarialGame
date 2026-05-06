def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obstacles)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        best_key = None
        best = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny): 
                continue
            # Go toward board center while increasing separation (deterministic fallback)
            center_dist = man(nx, ny, (w - 1) // 2, (h - 1) // 2)
            sep = man(nx, ny, ox, oy)
            key = (center_dist, -sep, dx, dy)
            if best_key is None or key < best_key:
                best_key, best = key, (dx, dy)
        return [best[0], best[1]]

    # Target: pick the resource that we can reach first; then compete using that choice.
    our_dists = [(man(sx, sy, rx, ry), i) for i, (rx, ry) in enumerate(resources)]
    our_dists.sort()
    target_i = our_dists[0][1]
    rx, ry = resources[target_i]

    best_key = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        my_after = man(nx, ny, rx, ry)
        opp_after = man(ox, oy, rx, ry)

        # If opponent is closer to the target than us, prioritize stealing turns:
        # reduce my distance and not let opponent become even more ahead.
        # Also add a slight repulsion from opponent to prevent direct race collisions.
        my_delta = my_after - man(sx, sy, rx, ry)
        opp_ahead = opp_after - my_after  # negative means opponent behind
        repulse = man(nx, ny, ox, oy)

        # Multi-resource sanity: ensure we don't ignore an even closer alternative after moving.
        alt_best = 10**9
        for j, (arx, ary) in enumerate(resources):
            d = man(nx, ny, arx, ary)
            if d < alt_best:
                alt_best = d
        alt_penalty = alt_best - my_after

        # Lower key is better
        key = (
            my_after,                # primary: get to target
            -opp_ahead,             # secondary: be closer than opponent
            my_delta,               # prefer moves that improve immediately
            alt_penalty,            # prefer not to abandon other near resources
            -repulse,               # prefer higher separation
            dx, dy
        )
        if best_key is None or key < best_key:
            best_key, best_move = key, (dx, dy)

    return [best_move[0], best_move[1]]