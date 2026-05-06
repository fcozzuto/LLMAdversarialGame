def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def eval_move(nx, ny):
        best_adv = -10**9
        best_sd = 10**9
        best_r = (0, 0)
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer
            # Prefer decisive advantage; then shorter for us; then deterministic by coord
            key = (adv, -sd, -rx, -ry)
            cur = (adv, -sd, -rx, -ry)
            if cur > (best_adv, -best_sd, -best_r[0], -best_r[1]):
                best_adv = adv
                best_sd = sd
                best_r = (rx, ry)
        if not resources:
            return (0, 0, 0, 0)
        # If we can't gain advantage, still prefer progress and avoid getting too close to opponent
        sep = man(nx, ny, ox, oy)
        return (best_adv, -best_sd, sep, -best_r[0] - 0.001 * best_r[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = eval_move(nx, ny)
        if best is None or score > best:
            best = score
            best_move = (dx, dy)

    # If all moves blocked, stay
    if best is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]