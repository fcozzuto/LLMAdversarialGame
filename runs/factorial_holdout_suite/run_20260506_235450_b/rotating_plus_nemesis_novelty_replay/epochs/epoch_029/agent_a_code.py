def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def step_towards(tx, ty, x, y):
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        return dx, dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx, dy = step_towards(tx, ty, sx, sy)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    # Pick a target with maximum race advantage, and slight bias toward nearer ones.
    best = None
    best_sc = -10**18
    for rx, ry in resources:
        self_d = abs(rx - sx) + abs(ry - sy)
        opp_d = abs(rx - ox) + abs(ry - oy)
        sc = (opp_d - self_d) * 1000 - self_d
        # Prefer targets not immediately blocked by obstacles near us
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny) and (nx, ny) == (rx, ry):
                sc += 200
                break
        if sc > best_sc:
            best_sc = sc
            best = (rx, ry)

    tx, ty = best

    # One-step lookahead: maximize progress toward our target while maintaining race advantage.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        self_d2 = abs(tx - nx) + abs(ty - ny)
        opp_d2 = abs(tx - ox) + abs(ty - oy)
        # Encourage reducing distance; discourage moving away; avoid "stuck" moves.
        val = (opp_d2 - self_d2) * 1200 - self_d2 * 2
        # Obstacle-adjacent penalty (discourages oscillations)
        for ax, ay in ((nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1)):
            if (ax, ay) in obstacles:
                val -= 20
        # Strongly prefer getting closer this turn
        val += (abs(tx - sx) + abs(ty - sy) - self_d2) * 50
        # Deterministic tie-break: lexicographic preference by cand order via index
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]