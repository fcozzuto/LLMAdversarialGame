def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_ev = ("evad" in self_role) or ("run" in self_role) or ("escap" in self_role)
    opp_ev = ("evad" in opp_role) or ("run" in opp_role) or ("escap" in opp_role)
    act_as_evader = self_ev or (not opp_ev and self_role == "" and not ("purs" in self_role or "hunt" in self_role))

    obs_list = observation.get("obstacles") or []
    obs = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def free_neighbors(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (dx or dy) and inb(nx, ny):
                c += 1
        return c

    # Greedy one-step look with simple "trap" awareness; deterministic tie-break by move order.
    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = cheb((nx, ny), (ox, oy))
        fn = free_neighbors(nx, ny)
        opp_after = (ox, oy)  # opponent moves next; we approximate by current positions only (deterministic, cheap)
        if act_as_evader:
            # Maximize distance, prefer not-too-tight spaces, and avoid moving into immediate capture range.
            score = (d, fn, - (1 if cheb((nx, ny), (ox, oy)) <= 0 else 0), dx, dy)
            # if capture_radius==0, "capture" means d==0; evader should avoid it hard
            if observation.get("capture_radius", 0) == 0 and d == 0:
                score = (-10**9, -10**9, -10**9, dx, dy)
            # choose lexicographically max by converting to tuple with consistent ordering
            if best is None or score > best_score:
                best_score, best = score, [dx, dy]
        else:
            # Pursuer: minimize distance; also prefer moves that keep options open.
            score = (-d, fn, dx, dy)
            if best is None or score > best_score:
                best_score, best = score, [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]