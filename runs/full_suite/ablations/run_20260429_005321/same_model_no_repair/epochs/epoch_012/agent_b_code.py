def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        tx = 1 if sx < w // 2 else (-1 if sx > w // 2 else 0)
        ty = 1 if sy < h // 2 else (-1 if sy > h // 2 else 0)
        return [tx, ty]

    # Choose a target resource: prioritize reaching it earlier than opponent; otherwise closest to us while preferring safe-ish cells.
    best = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        ahead = do - ds
        # Tie-break by preferring resources not surrounded by obstacles too tightly
        adj_obs = 0
        for dx, dy in deltas:
            nx, ny = rx + dx, ry + dy
            if inb(nx, ny) and (nx, ny) in obs:
                adj_obs += 1
        key = (-(ahead), ds, adj_obs, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # Evaluate each legal move with obstacle avoidance and 2-step distance reduction.
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d1 = cheb(nx, ny, tx, ty)

        # Lookahead one step more (still cheap, no BFS).
        best_d2 = 10**9
        for ddx, ddy in deltas:
            nnx, nny = nx + ddx, ny + ddy
            if not inb(nnx, nny) or (nnx, nny) in obs:
                continue
            d2 = cheb(nnx, nny, tx, ty)
            if d2 < best_d2:
                best_d2 = d2

        # Penalties: moving adjacent to obstacles and moving into opponent's "radius" around the target.
        adj = 0
        for ax, ay in deltas:
            px, py = nx + ax, ny + ay
            if inb(px, py) and (px, py) in obs:
                adj += 1
        opp_to_target = cheb(ox, oy, tx, ty)
        opp_if_block = cheb(ox, oy, nx, ny) <= max(1, opp_to_target - 1)

        score = (-d1) * 10 + (-best_d2) * 6 - adj * 7 - (30 if opp_if_block else 0)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]