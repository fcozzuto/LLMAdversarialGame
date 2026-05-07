def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = od - sd  # positive means we arrive earlier or at same speed
        key = (adv, -sd, -((tx + ty) & 1))
        if best is None or key > best[0]:
            best = (key, (tx, ty))
    target = best[1]
    tx, ty = target

    # Choose step minimizing distance to target with obstacle avoidance
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_step = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        # Prefer reducing distance; tie-break by aiming for same parity to reduce wandering
        k = (-d, -((nx + ny) & 1), 0 if (dx == 0 and dy == 0) else 1)
        if best_step is None or k > best_step[0]:
            best_step = (k, (dx, dy))

    if best_step is None:
        # All adjacent non-obstacle moves blocked: allow staying
        return [0, 0]
    return [int(best_step[1][0]), int(best_step[1][1])]