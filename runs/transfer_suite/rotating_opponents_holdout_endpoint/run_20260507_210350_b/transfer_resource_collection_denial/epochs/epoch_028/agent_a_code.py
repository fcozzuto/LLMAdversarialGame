def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turn = observation.get("turn_index", 0)

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        tx, ty = ((w - 1, 0) if ((sx + sy + turn) % 2 == 0) else (0, h - 1))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    best_r = resources[0]
    best_base = -10**18
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        share = (1 if rx == ox else 0) + (1 if ry == oy else 0)
        parity = 1 if ((rx + ry) % 2) == ((turn + sx + sy) % 2) else 0
        base = (do - ds) * 120 + share * 10 + parity * 3 - ds * 0.4
        if base > best_base:
            best_base = base
            best_r = (rx, ry)

    rx, ry = best_r
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy, nx, ny in candidates:
        ds2 = man(nx, ny, rx, ry)
        do = man(ox, oy, rx, ry)
        val = (do - ds2) * 120 - ds2 * 1.0
        if nx == rx and ny == ry:
            val += 1000
        if (nx + ny) % 2 == ((turn + rx + ry) % 2):
            val += 2
        if (nx, ny) == (ox, oy):
            val -= 50
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]