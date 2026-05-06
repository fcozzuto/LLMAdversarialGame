def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = cheb(nx, ny, tx, ty)
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    moves = []
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Evaluate by best achievable contest advantage after this move
    best_move = None
    best_score = None

    # Resource ordering to keep deterministic tie-breaking
    res_sorted = sorted(resources, key=lambda p: (p[0], p[1]))

    for dx, dy, nx, ny in moves:
        # Our closest-to-any-resource and opponent's closest-to-the-same-resource compete
        our_min = 10**9
        opp_min = 10**9
        best_adv = -10**9
        for rx, ry in res_sorted:
            if (rx, ry) in obs:
                continue
            od = cheb(ox, oy, rx, ry)
            sd = cheb(nx, ny, rx, ry)
            if sd < our_min:
                our_min = sd
            if od < opp_min:
                opp_min = od
            adv = od - sd
            if adv > best_adv:
                best_adv = adv

        # Prefer moves that make the opponent farther than us from some resource,
        # and also keep us converging (small our_min).
        score = best_adv * 100 - our_min * 3

        # Extra deny pressure: if opponent is extremely close to any resource,
        # prioritize immediate reduction of our minimum distance.
        if opp_min <= our_min:
            score += (our_min - opp_min) * 8

        # Deterministic tie-break: closer to resources, then prefer forward-ish (dx,dy lexicographic)
        tie = (our_min, dx, dy, nx, ny)
        if best_score is None or score > best_score or (score == best_score and tie < best_move):
            best_score = score
            best_move = tie
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]