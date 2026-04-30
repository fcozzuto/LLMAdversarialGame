def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set((int(x), int(y)) for x, y in obstacles)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    rx_list = [(int(x), int(y)) for x, y in resources if (int(x), int(y)) not in obs]

    # Pick a target where we are closer than opponent (or, if all lose, closest we can be)
    best_t = None
    best_key = None
    for rx, ry in rx_list:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (ds - do, ds, -rx, -ry)  # prefer smallest (our advantage), then nearest
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    if best_t is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best_t

    best_move = (0, 0)
    best_score = None

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obs:
                continue
            # Score: approach target, avoid giving opponent a faster line, keep distance from opponent
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            adv = (ds - do)
            dist_op = cheb(nx, ny, ox, oy)
            score = (adv * 20) + (ds * 1) - (dist_op * 0.5)
            # Slight deterministic bias to reduce dithering: prefer moves with smaller (abs dx+abs dy) first
            score += (abs(dx) + abs(dy)) * 0.01
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]