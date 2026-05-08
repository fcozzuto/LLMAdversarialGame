def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    role = (observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("escape" in role) or ("runner" in role) or ("flee" in role)

    # Deterministic tie-break order
    dirs_score_order = dirs[:]  # fixed

    best = None
    best_val = None
    best_aux = None

    for dx, dy in dirs_score_order:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d = abs(nx - ox) + abs(ny - oy)

        # Small obstacle-aware term to avoid dead-ends
        # Count blocked neighbors after move; evader prefers fewer, pursuer prefers fewer too (avoid invalid)
        blocked = 0
        free_moves = 0
        for adx, ady in dirs:
            tx, ty = nx + adx, ny + ady
            if 0 <= tx < w and 0 <= ty < h:
                if (tx, ty) in obst:
                    blocked += 1
                else:
                    free_moves += 1

        if evader:
            val = d
            aux = (free_moves, -blocked)
            better = (best is None) or (val > best_val) or (val == best_val and aux > best_aux)
        else:
            val = -d
            aux = (free_moves, -blocked)
            better = (best is None) or (val > best_val) or (val == best_val and aux > best_aux)

        if better:
            best = (dx, dy)
            best_val = val
            best_aux = aux

    if best is None:
        # Shouldn't happen; fallback to staying still
        return [0, 0]
    return [best[0], best[1]]