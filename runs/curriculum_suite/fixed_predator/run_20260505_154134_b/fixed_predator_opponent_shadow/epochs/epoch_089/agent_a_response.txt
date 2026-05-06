def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def neighbors(x, y):
        out = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obs:
                    out.append((nx, ny, dx, dy))
        return out

    def nearest_d(px, py):
        best = 10**9
        for rx, ry in resources:
            d = cheb(px, py, rx, ry)
            if d < best:
                best = d
        return best

    # Focus: win by getting to a resource before the opponent.
    # Score a move by (self_next_closer) - (opponent_next_closer), plus a small preference to avoid dead-ends.
    cand = neighbors(sx, sy)
    if not cand:
        return [0, 0]

    opp_next_base = nearest_d(ox, oy)

    best_mv = (0, 0)
    best_key = None
    for nx, ny, dx, dy in cand:
        self_d1 = nearest_d(nx, ny)

        # Opponent model: assume it will choose the move that minimizes its distance to the nearest resource.
        opp_best = None
        for tox, toy, _, _ in neighbors(ox, oy):
            d = nearest_d(tox, toy)
            if opp_best is None or d < opp_best:
                opp_best = d
        if opp_best is None:
            opp_best = opp_next_base

        # Lookahead escape: from next cell, count available exits (prefer more, avoid trapping).
        exits = len(neighbors(nx, ny))
        # Bias toward diagonal/forward progress deterministically via coordinates.
        progress_bias = (abs(nx - sx) + abs(ny - sy)) * 0.001

        key = (-(self_d1), (opp_best - self_d1), exits, -(nx + 17 * ny), -(dx == 0 and dy == 0))
        if best_key is None or key > best_key:
            best_key = key
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]