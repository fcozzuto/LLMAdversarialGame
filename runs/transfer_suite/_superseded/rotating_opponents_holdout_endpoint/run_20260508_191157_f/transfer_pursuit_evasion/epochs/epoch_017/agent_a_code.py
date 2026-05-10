def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obset = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) == 2)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obset

    def best_delta(candidates, scorer):
        best = None
        bestv = -10**18
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = scorer(nx, ny)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return list(best) if best is not None else [0, 0]

    env = observation.get("environment_name", "pursuit_evasion")
    role = observation.get("self_role", "pursuer")
    if env != "pursuit_evasion":
        return [0, 0]

    # Pursuer: move to reduce distance to opponent, prefer diagonal.
    if role == "pursuer":
        def closer(nx, ny):
            dx, dy = nx - ox, ny - oy
            # Chebyshev first (diagonal efficiency), then manhattan.
            return -max(abs(dx), abs(dy)) * 10 - (abs(dx) + abs(dy))
        candidates = []
        stepx = 0 if ox == sx else (1 if ox > sx else -1)
        stepy = 0 if oy == sy else (1 if oy > sy else -1)
        for ddx in [stepx, 0, -stepx]:
            for ddy in [stepy, 0, -stepy]:
                if ddx in (-1, 0, 1) and ddy in (-1, 0, 1):
                    candidates.append((ddx, ddy))
        # Ensure unique and include remaining directions
        seen = set()
        uniq = []
        for c in candidates + [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1)]:
            if c not in seen:
                seen.add(c)
                uniq.append(c)
        return best_delta(uniq, closer)

    # Evader: move to maximize distance from pursuer, avoid obstacles.
    def farther(nx, ny):
        dx, dy = nx - ox, ny - oy
        return max(abs(dx), abs(dy)) * 10 + (abs(dx) + abs(dy))
    stepx = 0 if ox == sx else (-1 if ox > sx else 1)
    stepy = 0 if oy == sy else (-1 if oy > sy else 1)
    candidates = []
    for ddx in [stepx, 0, -stepx]:
        for ddy in [stepy, 0, -stepy]:
            if ddx in (-1, 0, 1) and ddy in (-1, 0, 1):
                candidates.append((ddx, ddy))
    seen = set()
    uniq = []
    for c in candidates + [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1)]:
        if c not in seen:
            seen.add(c)
            uniq.append(c)
    return best_delta(uniq, farther)