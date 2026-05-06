def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(ax, ay, bx, by):
        ax -= bx
        ay -= by
        return abs(ax) + abs(ay)

    cells = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = r[0], r[1]
            if inb(rx, ry):
                cells.append((rx, ry))
    if not cells:
        return [0, 0]

    # Score a move by the best resource advantage it creates, plus a small anti-opponent term.
    best = (-10**18, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Prefer not stepping too close to opponent unless it improves resource advantage.
        opp_prox = -md(nx, ny, ox, oy)
        # Evaluate the top few resources by advantage.
        local_best = -10**18
        local_second = -10**18
        for rx, ry in cells:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Advantage: higher means we are closer than opponent.
            adv = (od - sd)
            # Slightly prioritize nearer targets when both are about equally contested.
            adv -= 0.08 * sd
            if adv > local_best:
                local_second = local_best
                local_best = adv
            elif adv > local_second:
                local_second = adv
        score = local_best + 0.35 * local_second + 0.12 * opp_prox

        # Tie-break deterministically: prefer smaller dx, then smaller dy, then stay if equal.
        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [best[1], best[2]]