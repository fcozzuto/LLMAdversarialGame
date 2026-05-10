def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def adj_count(nx, ny, sset):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (nx + dx, ny + dy) in sset:
                    c += 1
        return c

    best = None
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        target = (nx, ny)
        score = 0

        if target in self_t:
            score += 1
        elif target in opp_t:
            score += 7 + adj_count(nx, ny, self_t)  # flip & grow from frontier
            score += 2 * adj_count(nx, ny, opp_t)  # punish their cluster
        elif target in unclaimed:
            score += 5 + 2 * adj_count(nx, ny, self_t)  # outward expansion from our edge

        if adj_count(nx, ny, self_t) > 0:
            score += 2

        score -= 0.6 * (abs(nx - ox) + abs(ny - oy))  # keep distance from opponent

        # avoid dead-ends near obstacles a bit (local)
        obs_adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if not (0 <= px < w and 0 <= py < h) or (px, py) in obstacles:
                    obs_adj += 1
        score -= 0.15 * obs_adj

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]