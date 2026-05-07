def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = gw - 2 if sx < gw // 2 else 1
        ty = gh - 2 if sy < gh // 2 else 1
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Target selection: pick a resource where we have an advantage in distance vs opponent.
    best_res = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer bigger advantage (opponent farther), then smaller self distance, then deterministic position.
        key = (od - sd, -sd, -(rx * 31 + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_res = (rx, ry)

    tx, ty = best_res

    # Step selection: move towards target, but if blocked choose best alternative.
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        sd_next = cheb(nx, ny, tx, ty)

        # If we deviate, keep preference for paths that also don't help opponent too much.
        od_next = cheb(ox, oy, tx, ty)
        # Small bonus for not increasing distance to other high-value resources.
        # (deterministic: sample up to first 3 resources)
        bonus = 0
        lim = 3 if len(resources) > 3 else len(resources)
        for i in range(lim):
            rx, ry = resources[i]
            bonus -= 0.01 * cheb(nx, ny, rx, ry)

        score = (od_next - sd_next, -sd_next, bonus)
        # Convert tuple to comparable deterministic scalar-ish
        score_val = score[0] * 10_000 + score[1] * 100 + score[2]
        if score_val > best_score:
            best_score = score_val
            best_move = [dx, dy]

    return best_move