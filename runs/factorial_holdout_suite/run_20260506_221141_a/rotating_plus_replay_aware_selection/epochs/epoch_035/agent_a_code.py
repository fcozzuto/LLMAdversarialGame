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
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (gw - 1) // 2, (gh - 1) // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            return [dx, dy]
        for ddx, ddy in moves:
            nx, ny = sx + ddx, sy + ddy
            if legal(nx, ny):
                return [ddx, ddy]
        return [0, 0]

    best_val = -10**18
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        val = 0
        for rx, ry in resources:
            dS = cheb(nx, ny, rx, ry)
            dO = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach no later than opponent; penalize if opponent is closer.
            val += (dO - dS) * 10 - (1 if (nx == rx and ny == ry) else 0) * 2
            # Slight bias toward reducing our distance to any resource.
            val -= dS

        # If opponent is immediately adjacent to some resource, give extra priority to blocking it.
        block_bonus = 0
        for rx, ry in resources:
            if cheb(ox, oy, rx, ry) <= 1 and cheb(nx, ny, rx, ry) <= 2:
                block_bonus += 8
        val += block_bonus

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move