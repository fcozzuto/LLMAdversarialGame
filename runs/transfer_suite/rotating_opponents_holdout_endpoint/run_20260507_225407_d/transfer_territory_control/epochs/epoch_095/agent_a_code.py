def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_set = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_set = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = (0, 0)
    best_score = None
    best_tb = None

    base_self = len(self_set)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        gain = 0
        if (nx, ny) in opp_set:
            gain = 1 + (1 if (nx, ny) not in self_set else 0)
        elif (nx, ny) in unclaimed or (nx, ny) not in self_set and (nx, ny) not in opp_set:
            gain = 1

        # One-step simulated advantage: maximize controlled cells after move.
        # If flipping, assume opponent loses the cell we enter.
        sim_self = base_self + gain
        sim_diff = sim_self - len(opp_set) - (1 if (nx, ny) in opp_set and (nx, ny) not in self_set else 0)

        # Tie-breakers: prefer moving away from opponent slightly and toward center.
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_center = abs(nx - cx) + abs(ny - cy)
        tb = (-sim_diff, -gain, d_opp, d_center, dx, dy)

        if best_score is None or tb < best_tb:
            best_score = sim_diff
            best_tb = tb
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]