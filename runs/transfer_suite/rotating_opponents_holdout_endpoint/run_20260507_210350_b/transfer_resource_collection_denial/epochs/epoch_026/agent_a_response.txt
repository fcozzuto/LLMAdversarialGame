def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    ox, oy = observation["opponent_position"]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    if not resources:
        tx, ty = ((w - 1, 0) if (sx + sy) % 2 == 0 else (0, h - 1))
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    # Choose resource where we are relatively closer than opponent.
    best_r = None
    best_val = -10**18
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer reachable/contested advantage; break ties by smaller ds.
        val = (do - ds) * 100 - ds
        if ds == 0:
            val = 10**12
        if val > best_val:
            best_val = val
            best_r = (rx, ry)

    rx, ry = best_r
    # One-step best move toward target with obstacle risk and occasional opponent blocking.
    def obst_pen(x, y):
        p = 0
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d == 0:
                return 10**9
            if d == 1:
                p += 3
            elif d == 2:
                p += 1
        return p

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds_next = man(nx, ny, rx, ry)
        # Small tie-break toward staying useful: reduce our distance to chosen resource.
        score = -ds_next * 10 - obst_pen(nx, ny)
        # If opponent is also near this resource, try to reduce their advantage.
        do_next = man(ox, oy, rx, ry)
        score += (do_next - ds_next) * 2
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]