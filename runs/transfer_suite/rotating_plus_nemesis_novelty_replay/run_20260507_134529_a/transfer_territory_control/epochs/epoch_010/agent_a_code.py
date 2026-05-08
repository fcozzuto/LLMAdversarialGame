def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def pts(key):
        a = observation.get(key) or []
        out = []
        for p in a:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.append((x, y))
        return out

    obstacles = set(pts("obstacles"))
    candidates = pts("unclaimed_cells")
    if not candidates:
        candidates = pts("resources")
    if not candidates:
        candidates = [(w // 2, h // 2)]

    def man(a, b, c, d):  # |a-b|+|c-d|
        return abs(a - b) + abs(c - d)

    best = None
    best_adv = -10**18
    best_sd = 10**9
    for x, y in candidates:
        sd = man(x, sx, y, sy)
        od = man(x, ox, y, oy)
        adv = od - sd
        if adv > best_adv or (adv == best_adv and sd < best_sd) or (adv == best_adv and sd == best_sd and (x + y) < (best[0] + best[1] if best else 10**9)):
            best_adv, best_sd, best = adv, sd, (x, y)

    tx, ty = best
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    if not moves:
        return [0, 0]

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        sd = man(nx, tx, ny, ty)
        od = man(nx, ox, ny, oy)
        dist_center = abs(nx - w // 2) + abs(ny - h // 2)
        key = (sd, -od, dist_center, dx, dy)
        if best_key is None or key < best_key:
            best_key, best_move = key, (dx, dy)

    if best_key is None:
        # Fallback: step toward opponent if possible
        fallback = (1 if ox > sx else -1 if ox < sx else 0, 1 if oy > sy else -1 if oy < sy else 0)
        dx, dy = fallback
        nx, ny = sx + dx, sy + dy
        if dx == 0 and dy == 0:
            return [0, 0]
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
        # Otherwise stay
        return [0, 0]

    dx, dy = best_move
    return [int(dx), int(dy)]