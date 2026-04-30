def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]
    obst = {(p[0], p[1]) for p in obstacles}

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def safe_pen(nx, ny):
        if (nx, ny) in obst:
            return 10**9
        pen = 0
        for px, py in obstacles:
            dd = d2(nx, ny, px, py)
            if dd == 0:
                return 10**9
            if dd <= 1:
                pen += 80
            elif dd <= 4:
                pen += 25
            elif dd <= 9:
                pen += 8
        return pen

    best_move = (0, 0)
    best_val = -10**18

    if not resources:
        # fall back: move toward center while avoiding obstacles
        tx, ty = w // 2, h // 2
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            val = -safe_pen(nx, ny) - d2(nx, ny, tx, ty)
            if val > best_val:
                best_val, best_move = val, (dx, dy)
        return [best_move[0], best_move[1]]

    # pick best resource based on one-step advantage; then choose move that maximizes that resource's advantage
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        pen = safe_pen(nx, ny)
        if pen >= 10**8:
            continue

        move_val = -pen
        # Favor a resource where we are closer than the opponent, break ties by proximity to us.
        local_best = -10**18
        for rx, ry in resources:
            my = d2(nx, ny, rx, ry)
            op = d2(ox, oy, rx, ry)
            # Advantage: positive if we reduce/opponent farther; also encourage capturing exact resource.
            capture = 1200 if my == 0 else 0
            adv = (op - my)  # maximize
            proximity = -my  # also maximize closeness
            # Small obstacle-aware tie-break: prefer moves that don't "stall" near obstacles (already penalized).
            val = capture + 3 * adv + 0.2 * proximity
            if val > local_best:
                local_best = val
        # discourage staying still if moving can improve advantage
        still_pen = 0
        if dx == 0 and dy == 0:
            still_pen = 30
        move_val += local_best - still_pen

        if move_val > best_val:
            best_val, best_move = move_val, (dx, dy)

    return [best_move[0], best_move[1]]