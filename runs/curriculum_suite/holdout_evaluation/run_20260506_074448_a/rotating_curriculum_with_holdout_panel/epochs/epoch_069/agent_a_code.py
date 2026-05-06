def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list if p is not None and len(p) >= 2)
    resources = observation.get("resources") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    best = None
    best_adv = -10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        adv = do - ds
        if adv > best_adv or (adv == best_adv and (rx, ry) < best):
            best_adv = adv
            best = (rx, ry)
    if best is None:
        tx, ty = ox, oy
    else:
        tx, ty = best if best_adv >= 0 else (ox, oy)

    best_move = None
    best_cost = 10**9
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        cost = man(nx, ny, tx, ty)
        if cost < best_cost or (cost == best_cost and (dx, dy) < best_move):
            best_cost = cost
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]