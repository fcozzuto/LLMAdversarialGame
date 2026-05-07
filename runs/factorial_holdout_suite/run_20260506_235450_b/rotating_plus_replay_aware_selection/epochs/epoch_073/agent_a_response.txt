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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def mdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal or not resources:
        return [0, 0]

    # Deterministic ordering: prefer moves that keep x/y smaller in ties.
    legal.sort(key=lambda t: (t[2], t[3], t[0], t[1]))

    # Evaluate: maximize how much sooner we get there vs opponent; small preference for closeness.
    best_move = legal[0]
    best_val = None
    for dx, dy, nx, ny in legal:
        # If we can instantly reach a resource, prioritize it deterministically.
        instant = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if nx == rx and ny == ry:
                instant = (rx, ry)
                break
        if instant is not None:
            val = (10**9, -instant[0], -instant[1])
        else:
            best = None
            for r in resources:
                rx, ry = int(r[0]), int(r[1])
                sd = mdist(nx, ny, rx, ry)
                od = mdist(ox, oy, rx, ry)
                # Larger means better: we want od - sd to be large (deny opponent), then smaller sd.
                score = od - sd
                key = (score, -sd, -rx, -ry)  # deterministic tie-breaks
                if best is None or key > best:
                    best = key
            val = best
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]