def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose target that we can reach sooner and that also denies opponent reach
    resources = sorted(resources)
    best_val = None
    best_t = resources[0]
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        val = (od - sd) * 10 - sd
        # slight bias toward resources farther in our direction to prevent oscillation
        val += (tx - sx) + (ty - sy) if sd > 0 else 5
        if best_val is None or val > best_val:
            best_val = val
            best_t = (tx, ty)

    tx, ty = best_t
    cx = 0 if tx == sx else (1 if tx > sx else -1)
    cy = 0 if ty == sy else (1 if ty > sy else -1)

    deltas = []
    for ax in (-1, 0, 1):
        for ay in (-1, 0, 1):
            if ax < -1 or ax > 1 or ay < -1 or ay > 1:
                continue
            deltas.append((ax, ay))
    # deterministic order: move that best reduces cheb distance, then lexicographic
    def move_score(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            return -10**9
        return -cheb(nx, ny, tx, ty) * 100 + (dx == cx) * 5 + (dy == cy) * 3 - (dx == 0 and dy == 0) * 1

    best = None
    best_move = (0, 0)
    for dx, dy in sorted(deltas):
        sc = move_score(dx, dy)
        if best is None or sc > best:
            best = sc
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]