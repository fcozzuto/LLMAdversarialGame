def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    opp_pos = observation["opponent_position"]
    self_t = {tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2}
    opp_t = {tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2}
    unclaimed = {tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2}
    obstacles = {tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) >= 2}

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    opp_front = set()
    if opp_t:
        for (x, y) in opp_t:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) in unclaimed:
                        opp_front.add((nx, ny))

    # Fallback target: center; else chase opponent territory centroid/opponent position.
    if opp_t:
        ax = sum(x for x, _ in opp_t) / len(opp_t)
        ay = sum(y for _, y in opp_t) / len(opp_t)
    else:
        ax, ay = float(opp_pos[0]), float(opp_pos[1])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        v = 0.0
        if (nx, ny) in opp_t:
            v += 1e6  # immediate flip pressure
        if (nx, ny) in opp_front:
            v += 500  # deny opponent frontier expansion
        if (nx, ny) in unclaimed:
            # prefer moving toward center of the map and toward opponent mass
            v += 50 - (abs(nx - cx) + abs(ny - cy))
            v += 20 - (abs(nx - ax) + abs(ny - ay))

        # Guard/pressure balance: approach opponent when not already flipping
        if opp_t:
            d_opp = min(abs(nx - x) + abs(ny - y) for x, y in opp_t)
            v += 30 - d_opp
        else:
            v += 20 - (abs(nx - ax) + abs(ny - ay))

        # Slightly avoid stepping backward away from our nearest unclaimed/territory growth.
        if self_t:
            d_self = min(abs(nx - x) + abs(ny - y) for x, y in self_t)
            v -= 0.1 * d_self

        if v > bestv:
            bestv = v
            best_move = [dx, dy]
    return best_move