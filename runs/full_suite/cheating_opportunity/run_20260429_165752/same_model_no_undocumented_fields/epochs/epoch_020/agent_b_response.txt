def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    # If resources exist, try to secure the best "next" target by comparing distance with opponent.
    # Deterministic: break ties by preferring smaller dx, then smaller dy order in moves list.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if resources:
            # Value = closeness to a target while also being earlier than opponent toward it.
            # Use max over targets (best target we can race for next).
            cur_best = -10**18
            for rx, ry in resources:
                d_me = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                # Prefer targets where we are at least as close; otherwise penalize.
                race = (d_op - d_me)
                val = (-d_me * 10) + (race * 4)
                if val > cur_best:
                    cur_best = val
            # Slightly spread from opponent to reduce contest collisions
            opp_dist = cheb(nx, ny, ox, oy)
            total = cur_best + opp_dist * 0.2
        else:
            # No visible resources: drift toward opponent corner complement (opponent's vicinity).
            total = cheb(nx, ny, ox, oy) * 0.1
            total = -cheb(nx, ny, 7 - ox, 7 - oy)  # deterministic bias to explore opposite area

        if total > best_val:
            best_val = total
            best = (dx, dy)

    return [int(best[0]), int(best[1])]