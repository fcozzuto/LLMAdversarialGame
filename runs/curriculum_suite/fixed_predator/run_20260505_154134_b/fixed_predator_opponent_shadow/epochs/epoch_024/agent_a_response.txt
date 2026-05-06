def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def move_ok(x, y):
        return inb(x, y) and (x, y) not in obs

    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not move_ok(nx, ny):
            continue

        # Evaluate this move by the best resource advantage we can claim next.
        cur_best_adv = -10**9
        cur_best_sd = 10**9
        for cx, cy in resources:
            sd = cheb(nx, ny, cx, cy)
            od = cheb(ox, oy, cx, cy)
            adv = od - sd
            if adv > cur_best_adv or (adv == cur_best_adv and sd < cur_best_sd):
                cur_best_adv = adv
                cur_best_sd = sd

        # Secondary: softly prefer not letting opponent get closer to the chosen cell.
        # (deterministic constant weights)
        val = (cur_best_adv * 1000) - cur_best_sd
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]