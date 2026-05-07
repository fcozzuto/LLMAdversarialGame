def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for x, y in resources:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        # Prefer cells we can reach earlier; if not, still pick best advantage.
        key = (od - sd, -sd, -(x + y), x, y)
        if best is None or key > best_key:
            best = (x, y)
            best_key = key

    tx, ty = best
    step_dx = 0 if tx == sx else (1 if tx > sx else -1)
    step_dy = 0 if ty == sy else (1 if ty > sy else -1)

    moves = [(step_dx, step_dy), (step_dx, 0), (0, step_dy), (step_dx, -step_dy), (-step_dx, step_dy)]
    seen = set()
    for dx, dy in moves + [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]:
        if (dx, dy) in seen:
            continue
        seen.add((dx, dy))
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]

    return [0, 0]