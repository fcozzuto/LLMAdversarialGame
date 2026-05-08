def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = w // 2, h // 2

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            val = -10**15
        else:
            val = 0
            if (nx, ny) in opp_t:
                val += 2000  # flipping into opponent territory is highly valuable
                val += 5 * (1.0 / (1 + man(nx, ny, ox, oy)))
            if (nx, ny) in self_t:
                val += 20
            if (nx, ny) in unclaimed:
                val += 80
                # prefer grabbing unclaimed cells that are "safe" from immediate opponent frontier
                adj_opp = 0
                for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    if (nx + ax, ny + ay) in opp_t:
                        adj_opp += 1
                val -= 25 * adj_opp
                # also prefer moving toward center and away from opponent
                val += 8 * (man(nx, ny, ox, oy) - man(sx, sy, ox, oy))
                val += 6 * (-man(nx, ny, cx, cy))
            # mild preference to expand our territory boundary (unclaimed adjacent to us)
            if unclaimed:
                adj_self = 0
                for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    if (nx + ax, ny + ay) in self_t:
                        adj_self += 1
                val += 3 * adj_self
            # discourage staying if alternatives exist
            if dx == 0 and dy == 0:
                val -= 5
        if val > best_val:
            best_val = val
            best = [dx, dy]

    return [int(best[0]), int(best[1])]