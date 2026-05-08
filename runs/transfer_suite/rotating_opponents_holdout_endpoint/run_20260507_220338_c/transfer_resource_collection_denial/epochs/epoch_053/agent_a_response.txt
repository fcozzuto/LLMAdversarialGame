def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(p) for p in (observation.get("resources", []) or []) if tuple(p) not in obstacles]
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # Pick a target resource where we are relatively closer than the opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        advantage = od - sd  # positive if we are closer
        # Bias away from resources extremely near opponent to reduce "shared/contested" paths.
        contest_bias = cheb(ox, oy, rx, ry)
        # Prefer being able to reach soon; then maximize advantage.
        key = (advantage, -sd, -contest_bias, -(rx + 31 * ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Evaluate next step by minimizing our distance to the target, while avoiding obstacles and
    # slightly preferring moves that increase distance from opponent.
    def move_score(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        my = man(nx, ny, tx, ty)
        opp = man(nx, ny, ox, oy)
        # Also nudge toward progress: reduce our distance compared to staying.
        stay_dist = man(sx, sy, tx, ty)
        progress = stay_dist - my
        # Discourage stepping onto squares with fewer escape options (simple local mobility).
        mobility = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ax, ay = nx + dx, ny + dy
                if inb(ax, ay) and (ax, ay) not in obstacles:
                    mobility += 1
        return (progress * 10) + (-my) + (opp * 0.05) + (mobility * 0.02)

    best_move = (0, 0)
    best_ms = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            ms = move_score(nx, ny)
            if best_ms is None or ms > best_ms:
                best_ms = ms
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]