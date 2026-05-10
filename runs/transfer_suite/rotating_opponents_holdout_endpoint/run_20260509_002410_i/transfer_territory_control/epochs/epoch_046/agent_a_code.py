def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    opp_pos = observation.get("opponent_position") or [w - 1, h - 1]
    if not opp_t:
        opp_cent = opp_pos
    else:
        ax = sum(x for x, _ in opp_t) / len(opp_t)
        ay = sum(y for _, y in opp_t) / len(opp_t)
        opp_cent = (ax, ay)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2_point(x, y, p):
        dx = x - p[0]
        dy = y - p[1]
        return dx * dx + dy * dy

    def adj_cnt(cell, sset):
        x, y = cell
        c = 0
        for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            if (x + ddx, y + ddy) in sset:
                c += 1
        return c

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        n = (nx, ny)

        score = 0
        if n in opp_t:
            score += 100000  # guaranteed high priority capture
        else:
            if n in unclaimed:
                score += 5000
            if n in self_t:
                score += 500
            if not opp_t:
                score += -dist2_point(nx, ny, opp_cent) * 0.01

        # Frontier pressure: grow where we have nearby self control
        score += adj_cnt(n, self_t) * 80

        # Push away from opponent "center" unless capturing/near them
        score += -dist2_point(nx, ny, opp_cent) * 0.1

        # If close to opponent cells, slightly prefer moving towards them (to create captures)
        if opp_t:
            close = min(abs(nx - ox) + abs(ny - oy) for ox, oy in opp_t)
            score += max(0, 6 - close) * 40

        if score > best_score:
            best_score = score
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best