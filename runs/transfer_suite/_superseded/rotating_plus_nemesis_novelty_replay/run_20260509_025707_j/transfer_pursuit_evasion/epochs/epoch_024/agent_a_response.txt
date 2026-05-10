def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    if w < 2 or h < 2 or not isinstance(sp, (list, tuple)) or not isinstance(op, (list, tuple)) or len(sp) < 2 or len(op) < 2:
        return [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "pursuer").lower()
    is_evader = role == "evader"

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x, y, a, b):
        dx = abs(x - a)
        dy = abs(y - b)
        return dx if dx > dy else dy

    best = None  # (score, tie_x, tie_y, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        d = cheb(nx, ny, ox, oy)
        # Score meaning: higher is better for evader, lower is better for pursuer
        center_bias = (abs(nx - cx) + abs(ny - cy)) * 0.01
        if is_evader:
            # Prefer maximizing distance; also avoid edges a bit (via center bias)
            score = (-d) + center_bias
        else:
            # Prefer minimizing distance; also prefer not drifting too much from center
            score = (d) + center_bias

        # Deterministic tie-breaking: prefer smaller dx then smaller dy then lexicographic position
        key = (score, dx, dy, nx, ny)
        if best is None or key < best:
            best = key

    if best is None:
        return [0, 0]
    return [best[1], best[2]]