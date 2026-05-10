def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = -10**18
    best_move = [0, 0]

    if not resources:
        tx, ty = w - 1, h - 1
        if (sx + 1) < w: tx = w // 2
        if sx > w // 2: tx = 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Precompute opponent distances to resources
    opp_d = []
    for rx, ry in resources:
        opp_d.append((rx, ry, dist8(ox, oy, rx, ry)))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Our advantage: for each resource, prefer states where we are closer than opponent
        val = 0.0
        our_best = 10**9
        opp_best = 10**9
        tie_block = 0.0

        for rx, ry, od in opp_d:
            md = dist8(nx, ny, rx, ry)
            if md < our_best:
                our_best = md
            if od < opp_best:
                opp_best = od
            adv = od - md  # positive if we are closer
            # Emphasize near resources and being the first to arrive
            if md == 0:
                val += 40.0
            elif adv > 0:
                val += 8.0 * adv / (md + 1) + 1.2 * (1.0 / (md + 1))
            elif adv == 0:
                tie_block += 1.0 / (md + 1)
                val += 0.2 / (md + 1)
            else:
                val -= 4.0 * (-adv) / (md + 1)

        # If we can reach some resource earlier than opponent, strongly commit.
        if our_best < opp_best:
            val += 20.0 / (our_best + 1)
        else:
            val -= 10.0 / (our_best + 1)

        # Reduce ties: avoid moves that leave many equal-time resources.
        val -= 2.5 * tie_block

        # Deterministic tie-break: prefer smaller move magnitude, then closer to opponent's side imbalance
        move_mag = dx*dx + dy*dy
        if val > best or (val == best and (move_mag < (best_move[0]*best_move[0] + best_move[1]*best_move[1]))):
            best = val
            best_move = [dx, dy]

    return best_move