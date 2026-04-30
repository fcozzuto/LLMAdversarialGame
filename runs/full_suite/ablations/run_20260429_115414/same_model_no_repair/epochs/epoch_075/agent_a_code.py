def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set((x, y) for x, y in (observation.get("obstacles", []) or []))

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

    def obs_near(x, y):
        d = 10
        for ax, ay in obstacles:
            dd = cheb(x, y, ax, ay)
            if dd < d:
                d = dd
                if d == 0:
                    return 0
        return d

    if resources:
        best = None
        best_adv = -10**18
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            if adv > best_adv or (adv == best_adv and (rx, ry) < best):
                best_adv = adv
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = w // 2, h // 2

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    curr_adv = cheb(ox, oy, sx, sy) - cheb(sx, sy, ox, oy)  # unused except determinism
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            score = -10**12 - cheb(sx, sy, tx, ty)
        else:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Primary: win the race to target; Secondary: keep distance from obstacles
            near = obs_near(nx, ny)
            # Slight opponent pressure: prefer routes that reduce our relative advantage drop
            score = (do - ds) * 10 - ds - (2.5 / (near + 1)) * 10
            # Deterministic tie-break preference: move order then lex by move delta
            score = score + (0.01 * (dx + 1)) + (0.001 * (dy + 1)) + curr_adv * 0
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]