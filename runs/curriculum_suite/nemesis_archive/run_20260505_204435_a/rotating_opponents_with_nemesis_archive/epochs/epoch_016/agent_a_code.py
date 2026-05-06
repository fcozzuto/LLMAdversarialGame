def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def cheb(ax, ay, bx, by):
        ax = ax - bx; ay = ay - by
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    targets = []
    for r in resources:
        if isinstance(r, dict):
            pos = r.get("position", None)
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                targets.append((pos[0], pos[1]))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((r[0], r[1]))
    if not targets:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_dxdy = (0, 0)
    best_val = None

    # Heuristic: minimize (our_dist - opp_dist) to a contested resource;
    # then minimize our distance to finish quickly.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Also mildly avoid moves that increase our distance to the opponent (keeps us from getting kited).
        # (Opponent archetype: nearest_resource -> tends to pull toward specific resources; we mirror competition.)
        opp_press = cheb(nx, ny, ox, oy)

        best_for_move = None
        for rx, ry in targets:
            dsi = cheb(nx, ny, rx, ry)
            doi = cheb(ox, oy, rx, ry)
            # lower is better: negative means we can arrive earlier
            val = (dsi - doi) * 100 + dsi * 2 + (0 if dsi <= doi else 10) + opp_press * 0.01
            if best_for_move is None or val < best_for_move:
                best_for_move = val
        if best_for_move is None:
            continue
        if best_val is None or best_for_move < best_val:
            best_val = best_for_move
            best_dxdy = (dx, dy)
        elif best_for_move == best_val:
            # deterministic tie-break: prefer not moving if tied; else smallest |dx| then |dy|
            if (dx == 0 and dy == 0) and not (best_dxdy[0] == 0 and best_dxdy[1] == 0):
                best_dxdy = (dx, dy)
            else:
                if abs(dx) < abs(best_dxdy[0]) or (abs(dx) == abs(best_dxdy[0]) and abs(dy) < abs(best_dxdy[1])):
                    best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]