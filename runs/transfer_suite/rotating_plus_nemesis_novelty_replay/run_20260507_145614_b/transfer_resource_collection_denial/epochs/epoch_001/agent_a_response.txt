def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # Head toward center to avoid being stuck.
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestv = 10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if nx < 0 or nx >= w or ny < 0 or ny >= h: 
                    continue
                if (nx, ny) in obstacles: 
                    continue
                v = cheb(nx, ny, tx, ty)
                if v < bestv or (v == bestv and (dx, dy) < tuple(best)):
                    bestv = v
                    best = [dx, dy]
        return best

    # Pick target resource where we have a relative distance advantage.
    best_target = None
    best_key = None
    for rx, ry in sorted(resources):
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer being closer than opponent; tie-break by coordinate for determinism.
        key = (do - ds, -ds, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    rx, ry = best_target
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            # If moving would get you onto the resource, strongly prefer.
            onto = 1 if (nx, ny) == (rx, ry) else 0
            # Penalize giving the opponent an easier path by moving away from target.
            ns = cheb(nx, ny, rx, ry)
            no = cheb(ox, oy, rx, ry)
            # Slight preference for progress over diagonals that don't help (deterministic tie-break).
            val = (-(onto * 1000), ns - no, abs(dx) + abs(dy), dx, dy)
            candidates.append((val, [dx, dy]))

    candidates.sort(key=lambda t: t[0])
    return candidates[0][1]