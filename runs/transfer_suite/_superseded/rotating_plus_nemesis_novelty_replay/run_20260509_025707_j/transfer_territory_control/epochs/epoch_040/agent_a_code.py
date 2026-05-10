def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    self_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}
    ox, oy = observation["opponent_position"]

    opp_pts = list(opp_set)
    if not opp_pts:
        opp_pts = [(ox, oy)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def min_dist_to_opp(x, y):
        md = 10**9
        for px, py in opp_pts:
            d = abs(px - x) + abs(py - y)
            if d < md:
                md = d
        return md

    def adj_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in opp_set:
                    return True
        return False

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        if (nx, ny) in opp_set:
            score = -10**9 + min_dist_to_opp(nx, ny)  # huge avoid flipping
        else:
            dist = min_dist_to_opp(nx, ny)
            score = dist * 3.0
            if (nx, ny) in unclaimed:
                score += 8.0
                if not adj_opp(nx, ny):
                    score += 6.0
            if (nx, ny) in self_set:
                score -= 1.0  # prefer frontier expansion
            if adj_opp(nx, ny):
                score -= 5.0

        # tie-break deterministically by move order already in 'moves'
        if score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]