def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def clamp(x, y):
        if x < 0 or x >= w or y < 0 or y >= h:
            return None
        if (x, y) in obstacles:
            return None
        return (x, y)

    # If no resources, head toward center to reduce blocking potential
    if not resources:
        tx, ty = w // 2, h // 2
    else:
        # Target a resource that is close to us and far from opponent (denial bias)
        best = None
        best_val = None
        for rx, ry in resources:
            ds = abs(rx - sx) + abs(ry - sy)
            do = abs(rx - ox) + abs(ry - oy)
            # Use diagonal-capable distance approximation to match movement
            ds2 = max(abs(rx - sx), abs(ry - sy))
            do2 = max(abs(rx - ox), abs(ry - oy))
            val = (do2 - ds2) * 10 - ds2
            if best is None or val > best_val or (val == best_val and (rx, ry) < best):
                best = (rx, ry)
                best_val = val
        tx, ty = best

    # Evaluate one-step moves deterministically
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        p = clamp(nx, ny)
        if p is None:
            continue
        nx, ny = p
        ds = max(abs(tx - nx), abs(ty - ny))
        # Prefer moves that also reduce risk of opponent contesting the target
        do = max(abs(tx - ox), abs(ty - oy))
        opp_near = 1 if max(abs(nx - ox), abs(ny - oy)) <= 1 else 0
        # Tie-breaker prefers closer to opponent (blocking) when denial isn't possible
        # and then lexicographic move for determinism.
        score = (-ds * 100) + (opp_near * -20) + (do - ds) * 2
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]