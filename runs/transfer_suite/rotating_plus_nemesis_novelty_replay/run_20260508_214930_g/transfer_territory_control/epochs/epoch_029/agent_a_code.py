def choose_move(observation):
    w, h = observation.get("grid_width", 0), observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not dirs:
        return [0, 0]

    if unclaimed:
        targets = [(ux, uy) for ux, uy in unclaimed if inside(ux, uy)]
        if not targets:
            targets = [(ux, uy) for ux, uy in unclaimed]
    else:
        targets = [(ox, oy)]  # fallback: go pressure

    best_score = None
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # Evaluate by best target we can reach/claim relative to opponent
        score = -10**18
        for ux, uy in targets[:30]:
            d_self = abs(ux - nx) + abs(uy - ny)
            d_opp = abs(ux - ox) + abs(uy - oy)
            # Prefer closer to a target; if we are closer than opponent, boost
            rel = d_opp - d_self
            s = -d_self + (20 if rel > 0 else 0) + (rel // 2)
            if s > score:
                score = s
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]