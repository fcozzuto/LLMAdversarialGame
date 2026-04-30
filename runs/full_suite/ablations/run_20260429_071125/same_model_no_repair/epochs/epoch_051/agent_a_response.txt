def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Candidate resources: not just nearest; include a few spread-out options to avoid mirroring.
    # Use a combined key: closer to self, and also far from opponent to reduce direct contention.
    res = []
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        res.append((ds, do, rx, ry))
    if not res:
        return [0, 0]
    res.sort(key=lambda t: (t[0] - 0.6 * t[1], t[0] + t[1], t[2], t[3]))
    candidates = res[:6] if len(res) > 6 else res

    # For each move: (1) maximize how many resources become "closer to me than opponent" (win potential)
    # (2) minimize my distance to best candidate
    # (3) add a small "blocking" term: if I move adjacent to opponent towards resources, reduce access
    best = None
    best_val = -10**18

    for dx, dy, nx, ny in legal:
        win_count = 0
        close_score = 0
        opp_block = 0
        for ds0, do0, rx, ry in candidates:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if myd == 0:
                win_count += 1000
                close_score += 10**9
            if myd < opd:
                win_count += 1
                close_score += (opd - myd) * 200
            elif myd == opd:
                close_score -= 20

            # Blocking heuristic: being close to the midpoint-ish line between opponent and resource
            # discourages moves that leave the opponent a clear advantage.
            if myd <= 2 and cheb(ox, oy, rx, ry) <= 4:
                opp_block += 1

        # Also penalize moves that move me closer to opponent "in spirit" (contested corridor).
        my_to_opp = cheb(nx, ny, ox, oy)
        base = win_count * 1000 + close_score - 8 * my_to_opp + 35 * opp_block

        if base > best_val:
            best_val = base
            best = (dx, dy)

    return [int(best[0]), int(best[1])]