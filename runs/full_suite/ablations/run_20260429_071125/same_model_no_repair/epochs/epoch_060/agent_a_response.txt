def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)
    resources = observation.get("resources") or []

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    res = [(x, y) for (x, y) in resources if inb(x, y) and (x, y) not in obs]
    if not res:
        # Drift toward center but bias away from opponent
        cx, cy = (w - 1) // 2, (h - 1) // 2
        def center_score(nx, ny): return cheb(nx, ny, cx, cy) - 0.5 * cheb(nx, ny, ox, oy)
        best = max(legal, key=lambda t: -center_score(t[2], t[3]))
        return [best[0], best[1]]

    # Deterministic alternation: sometimes emphasize denial, sometimes racing
    remain = observation.get("remaining_resource_count", len(res))
    parity = (observation.get("turn_index", 0) + remain) % 2

    def obstacle_prox(nx, ny):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0: continue
                if (nx + ax, ny + ay) in obs:
                    c += 1
        return c

    best_move = None
    best_val = -10**18

    for dx, dy, nx, ny in legal:
        my_closest = min(cheb(nx, ny, rx, ry) for (rx, ry) in res)
        # Opponent closeness from its current position (race/denial approximation)
        opp_closest = min(cheb(ox, oy, rx, ry) for (rx, ry) in res)

        # Favor collecting sooner, and (when possible) making opponent reach later.
        if parity == 0:
            val = (opp_closest - my_closest) * 1000 - my_closest
        else:
            val = (opp_closest - my_closest) * 800 + (-my_closest * 20)

        # Slightly prefer safer cells away from obstacles
        val -= obstacle_prox(nx, ny) * 3

        # Tie-break deterministically: prefer smaller resource distance, then direction toward nearest resource
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]