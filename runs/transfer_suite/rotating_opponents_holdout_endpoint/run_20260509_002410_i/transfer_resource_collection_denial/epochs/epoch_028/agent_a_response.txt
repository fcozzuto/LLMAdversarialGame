def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def mdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if resources:
        best_move = None
        best_val = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            # Prefer moves that secure a resource before/with opponent, and avoid giving up easy steals.
            val = -10**9
            for rx, ry in resources:
                d_me = mdist(nx, ny, rx, ry)
                d_op = mdist(ox, oy, rx, ry)
                # Higher when we arrive earlier (or tie), strongly penalize when opponent is much closer.
                arrive_term = 0
                if d_me <= d_op:
                    arrive_term = 120 - 8 * d_me + 6 * (d_op - d_me)
                else:
                    arrive_term = -80 - 10 * (d_me - d_op)
                # Small bias toward nearer resources in general.
                val_cand = arrive_term - 2 * (d_me)
                if val_cand > val:
                    val = val_cand
            # Additional local pressure: don't let opponent get closer to our chosen direction.
            # (Deterministic, lightweight.)
            if val > -10**8:
                # If we can capture this turn (adjacent), boost slightly.
                if any((nx == rx and ny == ry) for rx, ry in resources):
                    val += 30
                if best_val is None or val > best_val:
                    best_val = val
                    best_move = [dx, dy]
        if best_move is not None:
            return best_move

    # Fallback: move toward center or along alternating lane to reduce interference
    tx, ty = w // 2, h // 2
    best = None
    bestd = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d = mdist(nx, ny, tx, ty)
        if bestd is None or d < bestd:
            bestd = d
            best = [dx, dy]
    return best if best is not None else [0, 0]