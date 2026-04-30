def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Choose a target that we can reach no later than the opponent when possible.
    best_list = []
    for r in resources:
        d1 = cheb(sx, sy, r[0], r[1])
        d2 = cheb(ox, oy, r[0], r[1])
        if d1 <= d2:
            best_list.append((d1, r[1], r[0], r))
    pool = best_list if best_list else [(cheb(sx, sy, r[0], r[1]), r[1], r[0], r) for r in resources]
    pool.sort()
    target = pool[0][3]
    tx, ty = target

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        myd = cheb(nx, ny, tx, ty)
        oppd = cheb(ox, oy, tx, ty)
        # If stepping onto a resource, strongly prefer it.
        on_resource = 1 if (nx, ny) in set(resources) else 0
        # Deterrence: prefer moves that increase opponent's distance to our target.
        score = (
            -on_resource,
            myd,
            -(cheb(nx, ny, ox, oy)),
            oppd - cheb(ox, oy, tx, ty),
            ny,
            nx,
        )
        if best is None or score < best[0]:
            best = (score, (dx, dy))

    if best is None:
        return [0, 0]
    dx, dy = best[1]
    return [int(dx), int(dy)]