def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    i_am_evader = ("evader" in role) or ("runner" in role) or ("evasion" in role) or ("escape" in role)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def mobility(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    best_score = None
    best_move = [0, 0]
    tie = 0

    # Deterministic tie-break order matches dirs order
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        mob = mobility(nx, ny)

        # Pursuer: minimize distance, prefer moves with higher mobility.
        # Evader: maximize distance, prefer moves with higher mobility; avoid corner trap near obstacles.
        if i_am_evader:
            # Slightly penalize being near obstacles to reduce local dead-ends.
            near_obs = 0
            for odx, ody in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                tx, ty = nx + odx, ny + ody
                if (tx, ty) in obstacles:
                    near_obs += 1
            score = (-d, -mob, near_obs)
            cand = score
            # maximize lexicographically over (-d, -mob, -nearObs) -> use negative for desired
            # Here we already used -d and -mob; smaller near_obs is better, so keep near_obs positive in tuple (lower better).
            # We'll compare manually by converting to a numeric key.
            key = (-(d) , mob, -near_obs)
        else:
            # Small obstacle proximity penalty to avoid bumping into blocks repeatedly.
            near_obs = 0
            for odx, ody in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                tx, ty = nx + odx, ny + ody
                if (tx, ty) in obstacles:
                    near_obs += 1
            key = (-d, mob, -near_obs)  # higher better

        if best_score is None or key > best_score:
            best_score = key
            best_move = [dx, dy]
            tie = 0
        elif key == best_score:
            # Deterministic: keep earlier dir due to dirs order, so do nothing.
            tie += 1

    return [int(best_move[0]), int(best_move[1])]