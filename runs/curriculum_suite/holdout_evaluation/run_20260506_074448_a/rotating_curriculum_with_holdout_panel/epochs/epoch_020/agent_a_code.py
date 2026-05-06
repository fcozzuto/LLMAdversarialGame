def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def interior(x, y):
        d = x
        if w - 1 - x < d:
            d = w - 1 - x
        if y < d:
            d = y
        if h - 1 - y < d:
            d = h - 1 - y
        return d

    if not resources:
        # Stay centeredish if no targets
        best = (None, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = interior(nx, ny)
            if sc > best[1]:
                best = ((dx, dy), sc)
        if best[0] is None:
            return [0, 0]
        return [best[0][0], best[0][1]]

    # Intercept/shadow: pick the move that maximizes (opponent_dist - our_dist) to some resource,
    # i.e., resources where we are relatively closer than the opponent.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Small tie-break: prefer moving toward interior, and slightly away from opponent congestion.
        base = 0.6 * interior(nx, ny) - 0.05 * man(nx, ny, ox, oy)
        best_res = -10**18
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            rel = opp_d - self_d  # positive means we are closer than opponent
            # Also prefer resources that are globally nearer (faster collection once intercepted)
            speed = -(0.08 * (self_d + opp_d))
            sc = rel + speed
            if sc > best_res:
                best_res = sc
        total = base + best_res
        if total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]