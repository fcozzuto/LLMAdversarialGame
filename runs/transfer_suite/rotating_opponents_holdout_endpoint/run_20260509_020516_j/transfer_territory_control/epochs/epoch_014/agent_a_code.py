def choose_move(observation):
    W = int(observation.get("grid_width", 0) or 0)
    H = int(observation.get("grid_height", 0) or 0)
    if W <= 0 or H <= 0:
        return [0, 0]

    def xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict) and "x" in v and "y" in v:
            return int(v["x"]), int(v["y"])
        return 0, 0

    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
    sx, sy = xy(observation.get("self_position", (0, 0)))
    ox, oy = xy(observation.get("opponent_position", (0, 0)))

    obstacles = set()
    for c in observation.get("obstacles") or []:
        x, y = xy(c)
        if 0 <= x < W and 0 <= y < H:
            obstacles.add((x, y))

    self_set = set(tuple(xy(p)) for p in (observation.get("self_territory") or []))
    opp_set = set(tuple(xy(p)) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(xy(p)) for p in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    best_score = -10**18
    best_move = (0, 0)

    def in_bounds(x, y):
        return 0 <= x < W and 0 <= y < H

    def adj_to_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in opp_set:
                    return True
        return False

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        dist_center = abs(nx - cx) + abs(ny - cy)
        dist_to_opp = abs(nx - ox) + abs(ny - oy)

        score = 0
        if (nx, ny) in opp_set:
            score += 100000
        if (nx, ny) in unclaimed:
            score += 1200
        if adj_to_opp(nx, ny):
            score += 160
        # Prefer cutting toward opponent when safe, but keep center pressure.
        score += 60 * (20 - dist_to_opp)
        score -= 4 * dist_center
        # Slightly prefer not wasting a turn when already surrounded by our cells.
        if (nx, ny) in self_set:
            score -= 10

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]