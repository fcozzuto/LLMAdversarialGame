def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    t = int(observation.get("turn_index", 0))
    oppx, oppy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_set = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_set = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    un_set = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def man(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax + ay

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    bestv = -10**18
    self_tc = int(observation.get("self_territory_count", 0))
    opp_tc = int(observation.get("opponent_territory_count", 0))
    leader_mode = (t % 10 == 0 and self_tc >= opp_tc)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in self_set:
            base = 2.0
        elif (nx, ny) in un_set:
            base = 5.0
        elif (nx, ny) in opp_set:
            base = 3.2  # attack/flip, but not as good as expanding unclaimed
        else:
            base = 1.0

        center_adv = -abs(nx - cx) - abs(ny - cy)
        opp_dist = man(nx, ny, oppx, oppy)
        self_dist = man(nx, ny, 0, 0) + man(nx, ny, w - 1, h - 1)  # encourages spreading, favors exits

        attack_bias = 0.0
        if (nx, ny) in opp_set:
            attack_bias = 1.6 if opp_dist <= max(2, (w + h) // 4) else 0.6

        if leader_mode:
            # Be more aggressive on leader bonus turn.
            base += 1.5 if (nx, ny) in opp_set else 0.0

        v = base + 0.55 * center_adv + 0.35 * opp_dist - 0.02 * self_dist + attack_bias
        if v > bestv or (v == bestv and [dx, dy] < best):
            bestv = v
            best = [dx, dy]

    return [int(best[0]), int(best[1])]