def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for c in (observation.get("obstacles", []) or []):
        try:
            x, y = c
            obstacles.add((int(x), int(y)))
        except Exception:
            pass

    self_set = set((int(x), int(y)) for x, y in (observation.get("self_territory", []) or []))
    opp_set = set((int(x), int(y)) for x, y in (observation.get("opponent_territory", []) or []))
    unclaimed_set = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        if (nx, ny) in opp_set:
            gain = 4.0  # flip opponent control
        elif (nx, ny) in unclaimed_set:
            gain = 3.0  # claim new territory
        elif (nx, ny) in self_set:
            gain = 1.2  # reinforce
        else:
            gain = 0.0  # likely unreachable/irrelevant

        dist_opp = abs(nx - ox) + abs(ny - oy)
        dist_center = abs(nx - cx) + abs(ny - cy)
        score = gain * 100.0 - dist_opp * 1.5 - dist_center * 0.02

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return best