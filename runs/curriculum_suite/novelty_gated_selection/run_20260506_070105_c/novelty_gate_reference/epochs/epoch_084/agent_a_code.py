def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose a target we are likely to reach first.
    best_t = resources[0]
    best_v = None
    for t in resources:
        ds = man((sx, sy), t)
        do = man((ox, oy), t)
        # prefer states where we have a distance advantage; slight bias toward closer targets
        v = (do - ds) - 0.25 * ds - 0.35 * (t[0] == ox and abs(t[1] - oy) <= 2)
        if best_v is None or v > best_v:
            best_v, best_t = v, t
    tx, ty = best_t

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Greedy step: maximize improvement toward target while not allowing immediate opponent gain.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        ds2 = man((nx, ny), (tx, ty))
        do2 = man((ox, oy), (tx, ty))
        # If opponent is much closer, prefer stepping to a nearby "alternate" resource where we regain advantage.
        alt_bonus = 0.0
        for t in resources:
            dsa = man((nx, ny), t)
            doa = man((ox, oy), t)
            advantage = doa - dsa
            if advantage > 1:
                alt_bonus = max(alt_bonus, 0.15 * advantage - 0.04 * dsa)
        # discourage moves that bring us adjacent to opponent (risk of sweep/contestation)
        opp_adj = 1.0 if max(abs(nx - ox), abs(ny - oy)) <= 1 else 0.0
        score = (do2 - ds2) - 0.15 * ds2 + alt_bonus - 0.9 * opp_adj
        if best_score is None or score > best_score:
            best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]