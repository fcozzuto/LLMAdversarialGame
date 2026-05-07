def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = int(sx + dx), int(sy + dy)
        if not valid(nx, ny):
            continue

        self_block = 0
        opp_adj = man(nx, ny, ox, oy)
        if opp_adj <= 1 and (dx != 0 or dy != 0):
            self_block = 6  # discourage moving into tight opponent pressure

        # Evaluate immediate resource advantage, plus small preference for nearer resources.
        score = 0
        local_best = -10**18
        local_best2 = -10**18
        for rx, ry in resources:
            rdx = int(rx)
            rdy = int(ry)
            ds = man(nx, ny, rdx, rdy)
            do = man(ox, oy, rdx, rdy)
            adv = do - ds  # positive means we are closer
            # primary: maximize guaranteed closeness advantage; secondary: minimize our distance
            cand = adv * 1000 - ds
            if cand > local_best:
                local_best2 = local_best
                local_best = cand
            elif cand > local_best2:
                local_best2 = cand

        # slight extra for having multiple competitive targets (denier-friendly)
        score = local_best + (local_best2 // 10) - self_block

        # If we can land on a resource, prioritize heavily (deterministic).
        if any((int(r[0]), int(r[1])) == (nx, ny) for r in resources):
            score += 10**6

        # Deterministic tie-break: prefer moves with smaller distance to opponent? (breaks symmetry)
        if score > best_score:
            best_score = score
            best = [dx, dy]
        elif score == best_score and best is not None:
            # Tie-break by lexicographic dx,dy for determinism
            if [dx, dy] < best:
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return best