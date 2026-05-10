def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = set(tuple(p) for p in (observation.get("resources") or []))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def md(nx, ny, ax, ay):
        dx = nx - ax
        if dx < 0:
            dx = -dx
        dy = ny - ay
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        s = 0
        # Prefer approaching opponent, but strongly prefer stepping onto resources.
        s += 20 if (nx, ny) in resources else 0
        s += -md(nx, ny, ox, oy)
        # Small preference to keep moving (reduce chance of getting stuck).
        if dx == 0 and dy == 0:
            s -= 1
        if best is None or s > best_score:
            best_score = s
            best = [dx, dy]

    if best is None:
        # Fallback: any in-bounds, non-obstacle move (including stay if possible).
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best