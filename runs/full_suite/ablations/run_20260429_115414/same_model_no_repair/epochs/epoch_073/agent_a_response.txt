def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((x, y) for x, y in obs_list)

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

    def passable(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_res = None
    best_adv = -10**18

    if resources:
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive means we're closer
            if adv > best_adv:
                best_adv = adv
                best_res = (rx, ry)
    else:
        best_res = (w // 2, h // 2)

    rx, ry = best_res
    best_move = (0, 0)
    best_val = -10**18

    # Prefer: move that reduces our distance to target while also reducing opponent advantage.
    # Add obstacle-avoidance via immediate passability and small steering from obstacle proximity.
    def obst_score(x, y):
        if not obstacles:
            return 0
        m = 99
        for px, py in obstacles:
            d = cheb(x, y, px, py)
            if d < m:
                m = d
        # farther is better; penalize being adjacent
        return -20 if m <= 1 else (-5 if m == 2 else 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not passable(nx, ny):
            continue
        ds = cheb(nx, ny, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Encourage securing (larger adv) and approaching target (smaller ds).
        adv = do - ds
        val = 1000 * adv - ds + obst_score(nx, ny)
        # If both are similarly good, bias toward moving closer to target along Chebyshev direction.
        if ds == cheb(sx, sy, rx, ry):
            val -= 2 * (abs(nx - rx) + abs(ny - ry))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]