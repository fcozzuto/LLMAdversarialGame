def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        res = [(w // 2, h // 2)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    parity = int(observation.get("turn_index", 0)) & 1
    center = (w // 2, h // 2)
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy
        if parity == 0:
            # Contest resources where we can arrive earlier than opponent.
            v = -10**18
            for rx, ry in res:
                ds = man(nx, ny, rx, ry)
                do = man(ox, oy, rx, ry)
                margin = do - ds  # higher is better
                cand = margin * 100 - ds - 2 * man(nx, ny, center[0], center[1])
                if cand > v:
                    v = cand
        else:
            # If not contesting, prioritize denying opponent's likely nearest target.
            # Favor moves that reduce our distance while also not letting them gain too much.
            v = -10**18
            for rx, ry in res:
                ds = man(nx, ny, rx, ry)
                do = man(ox, oy, rx, ry)
                cand = - (ds + 0.6 * do) + (do - ds) * 80 - 2 * man(nx, ny, center[0], center[1])
                if cand > v:
                    v = cand
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]