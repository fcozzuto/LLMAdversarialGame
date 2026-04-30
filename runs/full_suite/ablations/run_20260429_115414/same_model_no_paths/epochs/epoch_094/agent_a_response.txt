def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def target_priority(rx, ry):
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Win race: higher when ds is smaller than do; otherwise prefer resources still reachable quickly
        return (do - ds) * 1000 - ds * 2 + (rx + ry)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Prefer moving into best race target while simultaneously making our move reduce our distance and
    # (if possible) increase opponent distance to that same target.
    resources_sorted = sorted(resources, key=lambda t: (-target_priority(t[0], t[1]), cheb(ox, oy, t[0], t[1]), t[0], t[1]))
    top_targets = resources_sorted[:4]

    best_move = (0, 0)
    best_val = -10**18

    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inside(nx, ny):
            continue

        # Evaluate this move against top targets; pick the best outcome deterministically.
        move_val = -10**18
        for rx, ry in top_targets:
            ds2 = cheb(nx, ny, rx, ry)
            do2 = cheb(ox, oy, rx, ry)

            # Strongly favor turning a tie/near-loss into advantage; also avoid wasting steps.
            race_gain = (do2 - ds2) - (do2 - cheb(sx, sy, rx, ry))
            closer = cheb(sx, sy, rx, ry) - ds2

            # Slight anti-jitter: prefer lower absolute distance to resource.
            val = race_gain * 1200 + closer * 40 + (do2 - ds2) * 8 - ds2 * 3

            # If we are already winning the race, prioritize staying on that resource.
            if cheb(sx, sy, rx, ry) <= cheb(ox, oy, rx, ry):
                val += 25
            move_val = val if val > move_val else move_val

        # Tie-break: deterministic preference order based on position
        if move_val > best_val or (move_val == best_val and (nx, ny) < (best_move[0] + sx, best_move[1] + sy)):
            best_val = move_val
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]