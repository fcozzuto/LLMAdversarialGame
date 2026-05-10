def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_t = set(map(tuple, observation.get("self_territory", [])))
    opp_t = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    self_cnt = observation.get("self_territory_count", len(self_t))
    opp_cnt = observation.get("opponent_territory_count", len(opp_t))
    aggressive = 1.8 if opp_cnt >= self_cnt else 1.1

    best = [0, 0]
    best_v = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        pos = (nx, ny)

        v = 0.0
        if pos in opp_t:
            v += 1200.0 * aggressive
        elif pos in self_t:
            v += 8.0
        elif pos in unclaimed:
            v += 220.0
        else:
            v += 30.0  # likely unknown/owned-by-neither; still somewhat good

        # Strongly steer toward the center (opponent archetype tends to control center).
        dist_center = abs(nx - cx) + abs(ny - cy)
        v += 220.0 / (1.0 + dist_center)

        # Penalize moving away from opponent when we are ahead (to prevent overextension),
        # otherwise prefer proximity to seize flips.
        dist_opp = abs(nx - ox) + abs(ny - oy)
        if opp_cnt < self_cnt:
            v += 35.0 / (1.0 + dist_opp)  # mild, still take contact if close
        else:
            v += 70.0 / (1.0 + dist_opp)

        # Avoid getting stuck near obstacles: penalize moves with adjacent obstacle cells.
        adj_obs = 0
        for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            tx, ty = nx + ax, ny + ay
            if inb(tx, ty) and (tx, ty) in obstacles:
                adj_obs += 1
        v -= 9.0 * adj_obs

        if v > best_v:
            best_v = v
            best = [dx, dy]

    return best