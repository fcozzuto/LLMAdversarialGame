def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs
    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    best = [None, 0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        best_score = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = int(r[0]), int(r[1])
            if not (0 <= rx < w and 0 <= ry < h) or (rx, ry) in obs:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Favor resources where we have an immediate distance advantage; otherwise, minimize urgency we lose.
            # Also add mild penalty for moving far from all resources.
            closer = (od - sd)
            if closer >= 0:
                val = (0, -closer, sd)
            else:
                val = (1, sd - od, sd)
            if best_score is None or val < best_score:
                best_score = val
        if best_score is None:
            best_score = (2, man(nx, ny, ox, oy), man(nx, ny, sx, sy))
        key = (best_score[0], best_score[1], best_score[2], abs(dx) + abs(dy), dx, dy)
        if best[0] is None or key < best[0]:
            best[0], best[1], best[2] = key, dx, dy

    if best[0] is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]