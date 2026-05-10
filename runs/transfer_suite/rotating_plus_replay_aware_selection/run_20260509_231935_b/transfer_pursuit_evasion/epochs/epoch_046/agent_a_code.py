def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    opp_role = str(observation.get("opponent_role") or "").lower()
    pursuer = ("purs" in role) or ("chase" in role) or ("hunter" in role) or (role == opp_role and ("purs" in opp_role))
    # Fallback: if unclear, assume pursuer behavior (works well with capture bonus)
    if "evad" in role:
        pursuer = False

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    # Choose objective: pursuer minimize dist; evader maximize dist.
    # Deterministic tie-break: prefer moves with smaller dx, then dy by fixed ordering in moves.
    best_val = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)

        # Add mild obstacle-aware pressure: avoid stepping into "tight" spots.
        # Count available neighbors around next cell.
        k = 0
        for adx, ady in moves[1:]:
            tx, ty = nx + adx, ny + ady
            if legal(tx, ty):
                k += 1

        if pursuer:
            # Primary: smaller distance. Secondary: more mobility.
            val = (-d, -k, dx, dy)
        else:
            # Primary: larger distance. Secondary: more mobility.
            val = (d, -k, dx, dy)

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move