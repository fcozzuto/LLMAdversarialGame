def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(ox), int(oy)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    oppT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) // 2, (h - 1) // 2

    def val_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        s = 0
        if (x, y) in oppT:
            s += 180
        elif (x, y) in unclaimed:
            s += 75
        elif (x, y) in selfT:
            s += 12
        else:
            s += 35
        # Prefer expansion toward center
        dist_center = abs(x - cx) + abs(y - cy)
        dist_prev = abs(sx - cx) + abs(sy - cy)
        s += (dist_prev - dist_center) * 4
        # Prefer engaging opponent territory
        dist_opp = abs(x - ox) + abs(y - oy)
        s += (abs(sx - ox) + abs(sy - oy) - dist_opp) * 2
        # Avoid getting too far from opponent when we can flip
        if (x, y) not in oppT:
            s -= dist_opp * 0.2
        else:
            s += 10
        return s

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            v = -10**9
        else:
            v = val_cell(nx, ny)
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]