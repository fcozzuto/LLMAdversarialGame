def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_role = observation.get("self_role", "")
    opp_role = observation.get("opponent_role", "")
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)

    # Determine who is pursuer/evader relative to us
    is_pursuer = (self_role.lower() == "pursuer") or (opp_role.lower() == "evader")
    # If roles are unknown, assume pursuer to be safe
    if self_role == "" and opp_role == "":
        is_pursuer = True

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                candidates.append((dx, dy))

    # If somehow blocked, stay
    if not candidates:
        return [0, 0]

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # Greedy target: pursuer minimizes distance; evader maximizes distance
    best = None
    best_val = None
    # Deterministic tie-break: prefer moves with smaller |dx|+|dy| then lexicographic
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        d = dist2(nx, ny, ox, oy)
        if is_pursuer:
            val = d
        else:
            val = -d
        tie = (abs(dx) + abs(dy), dx, dy)
        key = (val, ) + ((-tie[0], tie[1], tie[2]) if not is_pursuer else (tie[0], tie[1], tie[2]))
        # Use explicit comparisons for determinism
        if best is None:
            best, best_val = (dx, dy), key
        else:
            if is_pursuer:
                if key < best_val:
                    best, best_val = (dx, dy), key
            else:
                if key > best_val:
                    best, best_val = (dx, dy), key

    return [int(best[0]), int(best[1])]