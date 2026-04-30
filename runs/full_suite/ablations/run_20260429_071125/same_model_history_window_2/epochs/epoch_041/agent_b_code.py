def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # deterministic tie-break: prefer "smaller" move lexicographically
    moves.sort(key=lambda t: (abs(t[0]) + abs(t[1]), t[0], t[1]))

    best = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # choose target resource that we can contest most (ours closer than opponent)
        best_t_adv = -10**18
        best_t = resources[0]
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - our_d  # positive means contesting
            if adv > best_t_adv:
                best_t_adv = adv
                best_t = (rx, ry)

        rx, ry = best_t
        our_d = cheb(nx, ny, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        # score: prioritize contest advantage; then reduce our distance;
        # also penalize letting opponent be extremely close to the same target.
        score = 3.0 * best_t_adv - 1.2 * our_d - 0.6 * (1 if cheb(nx, ny, ox, oy) <= 1 else 0) + 0.2 * (w + h - opp_d)

        # small extra: if we are significantly closer to any resource, keep pushing rather than retreating
        if best_t_adv <= 0:
            score -= 0.8 * our_d

        if score > best_val:
            best_val = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]