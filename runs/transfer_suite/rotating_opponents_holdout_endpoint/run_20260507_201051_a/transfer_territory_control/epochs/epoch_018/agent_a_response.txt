def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Opponent archetype tends to central-claim; contest the center deterministically.
    cx, cy = w // 2, h // 2
    candidates = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0) or True]
    # Choose a target: unclaimed closest to center but not too close to opponent.
    if unclaimed:
        def key(p):
            px, py = p
            dc = abs(px - cx) + abs(py - cy)
            do = abs(px - ox) + abs(py - oy)
            # prioritize center, then avoid opponent, then tie-break by coordinates
            return (dc, -do, px, py)
        tx, ty = min(unclaimed, key=key)
    else:
        # If no unclaimed, steer toward a point near center away from opponent.
        tx, ty = cx, cy

    best = (0, 0)
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dn_center = abs(nx - tx) + abs(ny - ty)
        dn_opp = abs(nx - ox) + abs(ny - oy)
        # Prefer reducing distance to target and increasing separation from opponent.
        score = (-dn_center, dn_opp, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
    return [int(best[0]), int(best[1])]