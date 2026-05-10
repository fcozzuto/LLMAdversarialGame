def choose_move(observation):
    env = observation.get("environment_name", "resource_collection")
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if env != "pursuit_evasion":
        return [0, 0]

    role = observation.get("self_role", "pursuer")
    if role != "pursuer":
        # Keep deterministic evasion: move to maximize distance and avoid obstacles.
        candidates = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
        best = None
        best_val = -10**9
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= W or ny < 0 or ny >= H:
                continue
            if (nx, ny) in obstacles:
                continue
            d = max(abs(nx - ox), abs(ny - oy))  # Chebyshev
            val = d
            if best is None or val > best_val:
                best_val = val
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    # Pursuer: obstacle-aware interception towards opponent and along its line.
    candidates = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    signx = 0 if ox == sx else (1 if ox > sx else -1)
    signy = 0 if oy == sy else (1 if oy > sy else -1)

    best = None
    best_val = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= W or ny < 0 or ny >= H:
            continue
        if (nx, ny) in obstacles:
            continue

        # Primary objective: minimize Chebyshev distance (diagonal-aware).
        d = max(abs(nx - ox), abs(ny - oy))

        # Secondary: try to keep moving along the direct line to opponent.
        line_align = (1 if dx == signx else 0) + (1 if dy == signy else 0)

        # Tertiary: avoid moving "away" from opponent when possible.
        away = (1 if (dx == -signx and signx != 0) else 0) + (1 if (dy == -signy and signy != 0) else 0)

        # If direct step is blocked (by walls/obstacles), prefer the move that best reduces distance.
        # Deterministic tie-breaking: lexicographic on (line_align, -away, -d) via final scoring.
        val = (-d) * 1000 + line_align * 10 - away

        if best is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])] if best is not None else [0, 0]