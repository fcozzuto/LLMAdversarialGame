def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_t = set(map(tuple, observation.get("self_territory", [])))
    opp_t = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    self_cnt = observation.get("self_territory_count", len(self_t))
    opp_cnt = observation.get("opponent_territory_count", len(opp_t))

    aggressive = 1.8 if opp_cnt >= self_cnt else 1.1
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = (0, 0)
    best_v = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        target = (nx, ny)
        if target in opp_t:
            v = 120.0 * aggressive - 0.2 * man(nx, ny, ox, oy)
        else:
            d_opp = man(nx, ny, ox, oy)
            d_ctr = abs(nx - cx) + abs(ny - cy)
            v = 8.0 * (1 if target in unclaimed else 0) - 1.3 * d_opp - 0.35 * d_ctr
            if target in self_t:
                v -= 1.2  # prefer expansion/contest over staying

            # avoid stepping into squares adjacent to our own edge that give opponent a quick recapture
            danger = 0
            for adx, ady in moves:
                ax, ay = nx + adx, ny + ady
                if inb(ax, ay) and (ax, ay) in opp_t:
                    danger += 1
            v -= 1.8 * danger if aggressive < 1.5 else 0.9 * danger

        if v > best_v:
            best_v = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]