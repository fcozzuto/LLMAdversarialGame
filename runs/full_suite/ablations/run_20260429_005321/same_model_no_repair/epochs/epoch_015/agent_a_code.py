def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {(p[0], p[1]) for p in obstacles}

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, x, y):
        dx = a - x
        if dx < 0: dx = -dx
        dy = b - y
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    # If resource is adjacent, move onto it.
    if resources:
        best_adj = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            if max(abs(rx - sx), abs(ry - sy)) <= 1:
                if best_adj is None or (dist(ox, oy, rx, ry) - dist(sx, sy, rx, ry), rx, ry) > (best_adj[0], best_adj[1], best_adj[2]):
                    best_adj = (dist(ox, oy, rx, ry) - dist(sx, sy, rx, ry), rx, ry)
        if best_adj is not None:
            rx, ry = best_adj[1], best_adj[2]
            dx = 0 if rx == sx else (1 if rx > sx else -1)
            dy = 0 if ry == sy else (1 if ry > sy else -1)
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]

    # Choose a target that maximizes how much closer we are than opponent.
    # If tie, prefer nearer target for us, then deterministically by coordinates.
    tx, ty = (w - 1, h - 1)
    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            score = (do - ds, -ds, -rx, -ry)  # higher do-ds, then smaller ds, then deterministic
            if best is None or score > best[0]:
                best = (score, rx, ry)
        if best is not None:
            tx, ty = best[1], best[2]

    # One-step greedy toward target with opponent-aware tie-break and obstacle avoidance.
    best_move = (None, None)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_self = dist(nx, ny, tx, ty)
        d_opp = dist(ox, oy, tx, ty)
        closer = d_self == 0
        # Prefer reducing distance to our target; also prefer staying ahead of opponent.
        key = (
            1 if closer else 0,
            (d_opp - d_self),     # higher => we are relatively closer
            -d_self,              # higher => smaller self distance
            -abs(nx - ox) - abs(ny - oy),  # deterministic "spread"
            nx,
            ny
        )
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]