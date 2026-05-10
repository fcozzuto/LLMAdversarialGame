def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    my_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def adj_to_opp(p):
        x, y = p
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in opp_set:
                        return True
        return False

    frontier = [p for p in unclaimed if adj_to_opp(p)]
    if frontier:
        target = min(frontier, key=lambda p: dist((sx, sy), p))
    else:
        opp_list = list(opp_set)
        target = min(opp_list, key=lambda p: dist((sx, sy), p)) if opp_list else (sx, sy)

    best = None
    best_score = -10**18
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        p = (nx, ny)
        score = 0
        if p in opp_set:
            score += 1000
        if p in unclaimed:
            score += 30
            if adj_to_opp(p):
                score += 40
        if p in my_set:
            score += 5
        score += -2 * dist(p, target)
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]