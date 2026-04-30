def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy))
    if not candidates:
        return [0, 0]
    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Prefer moving to a resource we can reach sooner than opponent.
    # Tie-break deterministically by position.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy

        move_score = 0
        for r in resources:
            ds = dist((nx, ny), r)
            do = dist((ox, oy), r)
            adv = do - ds  # positive means we are closer
            # Primary: closeness advantage
            s = adv * 100
            # Secondary: prefer nearer targets even if not advantage
            s -= ds
            # Tertiary deterministic: prefer lower coordinates
            s -= (r[0] * 0.01 + r[1] * 0.001)
            # Strongly prefer taking a resource immediately
            if (nx, ny) == (r[0], r[1]):
                s += 10000
            # Discourage stepping near opponent when we can't secure a resource
            if adv <= 0 and do <= 2:
                s -= 5
            if s > move_score:
                move_score = s

        if move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)
        elif move_score == best_score:
            # Deterministic tie-break: smallest dx, then smallest dy
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]