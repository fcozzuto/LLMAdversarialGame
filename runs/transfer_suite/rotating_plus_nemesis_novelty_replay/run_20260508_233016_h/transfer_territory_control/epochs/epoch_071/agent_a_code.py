def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def mindist_to_list(x, y, lst):
        if not lst:
            return 10**9
        md = 10**9
        for px, py in lst:
            d = abs(x - px) + abs(y - py)
            if d < md:
                md = d
        return md

    best_move = (0, 0)
    best_score = -10**18
    opp_d = abs(sx - ox) + abs(sy - oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_un = mindist_to_list(nx, ny, unclaimed)
        score = 0
        score += (0 if d_un >= 10**8 else -d_un)
        score += 2 * (d_opp - opp_d)
        if (nx, ny) == (ox, oy):
            score -= 10**6
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]