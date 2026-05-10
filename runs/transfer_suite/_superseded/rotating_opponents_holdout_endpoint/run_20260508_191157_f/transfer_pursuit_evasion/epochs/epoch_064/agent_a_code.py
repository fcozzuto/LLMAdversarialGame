def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs_set = {(p[0], p[1]) for p in obstacles}
    role = (observation.get("self_role") or "pursuer").lower()
    pursuer = role == "pursuer"

    cands = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def neighbor_free_count(x, y):
        # more free neighbors => safer/easier to maneuver around obstacles
        cnt = 0
        for dx, dy in cands:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs_set:
                cnt += 1
        return cnt

    # target corner preference (deterministic)
    best_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    if pursuer:
        best_corner = min(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    best = (0, 0)
    best_sc = None
    for dx, dy in cands:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        d = cheb(nx, ny, ox, oy)
        # obstacle proximity penalty: discourage being boxed in
        nf = neighbor_free_count(nx, ny)
        corner_bias = -cheb(nx, ny, best_corner[0], best_corner[1])  # closer to desired corner is better
        # scoring: capture prefers exact match (d==0)
        if pursuer:
            sc = (1000 if d == 0 else 0) - 10 * d + 2 * nf + 0.1 * corner_bias
            better = (best_sc is None) or (sc > best_sc) or (sc == best_sc and (dx, dy) < best)
        else:
            sc = (1000 if d != 0 else -1000) + 10 * d + 2 * nf + 0.1 * corner_bias
            better = (best_sc is None) or (sc > best_sc) or (sc == best_sc and (dx, dy) < best)
        if better:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]