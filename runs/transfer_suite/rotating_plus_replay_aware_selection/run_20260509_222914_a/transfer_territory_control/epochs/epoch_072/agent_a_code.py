def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_ter = set(map(tuple, observation.get("self_territory") or []))
    opp_ter = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    target_x, target_y = (w - 1) / 2.0, (h - 1) / 2.0

    prev_to_target = dist(sx, sy, int(target_x), int(target_y))
    prev_to_opp = dist(sx, sy, ox, oy)

    best_move = (0, 0)
    best = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in unclaimed:
            score += 10
        elif (nx, ny) in self_ter:
            score += 3
        elif (nx, ny) in opp_ter:
            score += 6

        # Prefer moves that open space nearby
        adj_unclaimed = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                axx, ayy = nx + ax, ny + ay
                if inb(axx, ayy) and (axx, ayy) in unclaimed:
                    adj_unclaimed += 1
        score += adj_unclaimed * 2

        # Move toward center to claim more territory over time
        new_to_target = dist(nx, ny, int(target_x), int(target_y))
        score += (prev_to_target - new_to_target) * 2

        # If entering opponent territory, be slightly aggressive; otherwise avoid getting too close
        new_to_opp = dist(nx, ny, ox, oy)
        if (nx, ny) in opp_ter:
            score += (prev_to_opp - new_to_opp) * 2
        else:
            score += (new_to_opp - prev_to_opp) * 1

        if score > best:
            best = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]