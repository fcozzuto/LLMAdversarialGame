def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles", []) or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def safe(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or role.endswith("e")
    is_pursuer = ("pursuer" in role) or role.endswith("p")

    # Deterministic bias: alternate between two corner targets to reduce predictability.
    ti = int(observation.get("turn_index", 0) or 0)
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    target = corners[ti % 4] if (ti % 2 == 0) else corners[(ti + 1) % 4]

    def score_for(nx, ny):
        # distance objective + obstacle/wall penalty and local mobility for smoother motion
        d = abs(nx - ox) + abs(ny - oy)
        # encourage heading toward/away from target depending on role
        td = abs(nx - target[0]) + abs(ny - target[1])
        # mobility: prefer positions with more options
        mob = 0
        for dx, dy in moves:
            x2, y2 = nx + dx, ny + dy
            if safe(x2, y2):
                mob += 1
        # wall/obstacle avoidance is ensured by safe(); this just breaks ties
        tiebreak = (mob, -td if is_evader else -td)
        if is_evader:
            return (d * 100 + mob * 3) + (-td)
        elif is_pursuer:
            return (-(d * 100) + mob * 3) + (-td)
        else:
            # If role unknown, default to pursuer-like
            return (-(d * 100) + mob * 3) + (-td)

    best = None
    best_val = None
    # Deterministic move ordering bias toward reducing boundary hits: prefer staying inside via ordering
    order = sorted(moves, key=lambda m: (m[0] == 0 and m[1] == 0, abs(m[0]) + abs(m[1]), m[0], m[1]))
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        val = score_for(nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        # fallback: attempt safe move with max mobility
        best_mob = -1
        best = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not safe(nx, ny):
                continue
            mob = 0
            for dx2, dy2 in moves:
                x2, y2 = nx + dx2, ny + dy2
                if safe(x2, y2):
                    mob += 1
            if mob > best_mob:
                best_mob = mob
                best = [dx, dy]
    return [int(best[0]), int(best[1])]