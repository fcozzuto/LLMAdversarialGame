def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))

    best_move = (0, 0)
    best_val = None

    def resource_value(nx, ny):
        # Race-first: prefer resources where we beat opponent; then faster; then closer overall.
        best = (-10**9, None)
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Encourage immediate capture and securing multiple turns by reducing distance.
            win_gap = (do - ds)
            val = (win_gap * 1000) - (ds * 10) + (do - ds) * 2
            # Deterministic tiebreak using coordinates (keeps policy stable).
            val += -(rx + ry) * 0.001
            if val > best[0]:
                best = (val, (rx, ry))
        return best[0]

    # If we can capture a resource now, do it deterministically.
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if rx == sx and ry == sy:
            return [0, 0]

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        v = resource_value(nx, ny)
        # Secondary deterministic preference: maximize immediate improvement in (self - opp) distance.
        if best_val is None or v > best_val:
            best_val = v
            best_move = (dx, dy)
        elif v == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]