def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [W - 1, H - 1]) or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        tx, ty = resources[0]
        best = cheb(sx, sy, tx, ty)
        for x, y in resources[1:]:
            d = cheb(sx, sy, x, y)
            if d < best or (d == best and (x < tx or (x == tx and y < ty))):
                best, tx, ty = d, x, y
    else:
        center = ((W - 1) // 2, (H - 1) // 2)
        remaining = observation.get("remaining_resource_count", None)
        if remaining is not None and int(remaining) <= 0:
            tx, ty = ox, oy
        else:
            dcent = cheb(sx, sy, center[0], center[1])
            dop = cheb(sx, sy, ox, oy)
            tx, ty = (ox, oy) if dop <= dcent else center

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dist = cheb(nx, ny, tx, ty)
        score = (dist, -cheb(nx, ny, ox, oy), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]