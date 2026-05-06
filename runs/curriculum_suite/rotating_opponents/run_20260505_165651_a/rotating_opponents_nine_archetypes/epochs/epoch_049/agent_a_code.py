def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    if not moves:
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    center_pen = king_dist

    best_move = (0, 0)
    best_val = -10**18

    # If no resources, drift toward center while avoiding obstacles.
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            v = -center_pen(nx, ny, cx, cy)
            if v > best_val:
                best_val = v
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Prefer resource squares where we are closer than opponent; otherwise position to contest.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        val = 0.0
        # contest the best available resource from this candidate square
        local_best = -10**18
        for rx, ry in resources:
            our_d = king_dist(nx, ny, rx, ry)
            opp_d = king_dist(ox, oy, rx, ry)

            # Main: win/contest advantage.
            adv = opp_d - our_d  # positive => we can reach sooner/tie-break
            # Reward closeness and strong advantage more than raw closeness.
            v = (adv * 12.0) + (1.0 / (our_d + 1.0)) * 2.5
            # Slightly discourage moving away from all resources.
            v -= (our_d * 0.25)

            # Add a small nudge to reduce opponent's immediate advantage if close.
            # (tie breaker: if adv is small/negative, keep pressure near opponent-reachable targets)
            v += (-adv if adv < 0 else 0.0) * 0.15

            if v > local_best:
                local_best = v

        # Also keep some central/interception pressure vs center_rush style.
        local_best += -center_pen(nx, ny, cx, cy) * 0.6

        if local_best > best_val:
            best_val = local_best
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]