def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    opp_set = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                opp_set.add((x, y))

    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.add((x, y))

    def neighbors8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    yield nx, ny

    def edge_bias(x, y):
        return (1 if x == 0 or x == w - 1 else 0) + (1 if y == 0 or y == h - 1 else 0)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        in_opp = (nx, ny) in opp_set
        adj_opp = 0
        for ax, ay in neighbors8(nx, ny):
            if (ax, ay) in opp_set:
                adj_opp = 1
                break
        is_unclaimed = (nx, ny) in unclaimed
        dist_op = abs(nx - ox) + abs(ny - oy)

        score = 0
        score += 200 if in_opp else 0
        score += 35 if adj_opp else 0
        score += 12 * edge_bias(nx, ny)
        score += 6 if is_unclaimed else 0
        score += -dist_op

        if (best is None) or (score > best_score) or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]