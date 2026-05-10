def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unT = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def manhattan(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        # Contest: flipping opponent territory is highest priority.
        base = 0
        if (nx, ny) in opT:
            base += 8
        elif (nx, ny) in unT:
            base += 3
        elif (nx, ny) in selfT:
            base += 1

        # Reduce distance to opponent while aiming for contest/expansion.
        d_to_op = manhattan(nx, ny, ox, oy)
        base += max(0, 6 - d_to_op)

        # Prefer moves that are closer to unknown expansion zones (unclaimed nearby).
        adj_un = 0
        for adx, ady in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            ax, ay = nx + adx, ny + ady
            if in_bounds(ax, ay) and (ax, ay) in unT:
                adj_un += 1
        base += adj_un

        # Small penalty for stepping away from own territory to avoid lone wandering.
        if (nx, ny) not in selfT and manhattan(nx, ny, sx, sy) > 5:
            base -= 2

        if base > best_score:
            best_score = base
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best