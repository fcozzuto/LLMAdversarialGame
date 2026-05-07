def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    res = [(int(r[0]), int(r[1])) for r in resources]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic tie-break by fixed ordering above.

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate next position: prefer being closer to a resource than the opponent,
        # otherwise reduce opponent lead; also discourage being trapped.
        candidate = -10**18
        for rx, ry in res:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            # Primary: lead/contest margin. Secondary: closer distance.
            margin = od - sd
            val = margin * 1000 - sd
            if sd == 0:
                val += 10**7  # immediate collection
            # Mild repulsion from obstacles nearby
            for ex, ey in obstacles:
                md = abs(nx - ex) + abs(ny - ey)
                if md == 1:
                    val -= 5
            candidate = max(candidate, val)

        # Add small preference to moves that don't increase distance to current best resource
        # by using opponent comparison.
        if candidate > (best[0] if best else -10**18):
            best = (candidate, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]