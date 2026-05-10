def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((int(x), int(y)) for x, y in obstacles_list)
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def step_valid(nx, ny):
        if not inb(nx, ny):
            return False
        if (nx, ny) in obstacles:
            return False
        return True

    def risk(x, y):
        r = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    r += 1
        return r

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if step_valid(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Score candidate by being closer to resources where we can likely arrive first.
    # Also penalize giving opponent too strong access by maximizing our advantage.
    best = None
    best_score = -10**18
    for dx, dy, nx, ny in moves:
        rs = 0
        for rx, ry in resources:
            dS = cheb(nx, ny, rx, ry)
            dO = cheb(ox, oy, rx, ry)
            # "Win chance" term: only count if we are not behind too badly.
            win = dO - dS
            if win > 0:
                rs += 12 * win - dS
            else:
                rs += 2 * win - 2 * dS
        # Additional small preference for immediate collection cells and safety.
        immediate = 0
        if cheb(nx, ny, nx, ny) == 0:
            pass
        # If we are on a resource now, strongly favor.
        if (nx, ny) in set((int(x), int(y)) for x, y in resources):
            rs += 10**6
        rs -= 5 * risk(nx, ny)

        if rs > best_score or (rs == best_score and (dx, dy) < (best[0], best[1]) if best else False):
            best_score = rs
            best = (dx, dy)

    return [int(best[0]), int(best[1])]