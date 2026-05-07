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

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_move = (0, 0)
    best_val = -10**18

    # Evaluate each possible one-step move by the best resource we could pursue from the resulting cell,
    # strongly preferring resources we can reach strictly sooner than the opponent.
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        pos_val = -10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive => we are closer
            # If we are behind (adv negative), still pick the least-bad option, but discourage certainty loss.
            sc = adv * 220 - sd
            if (rx, ry) == (ox, oy):
                sc -= 1200  # avoid "chasing" the opponent's current exact spot
            # Prefer lower self distance on ties deterministically
            if sc > pos_val:
                pos_val = sc
            elif sc == pos_val and sd < man(nx, ny, resources[0][0], resources[0][1]):
                pos_val = sc
        if pos_val > best_val:
            best_val = pos_val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]