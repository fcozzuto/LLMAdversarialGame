def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = observation.get("obstacles", [])
    obs = set()
    for p in obstacles:
        if p is not None and len(p) == 2:
            obs.add((p[0], p[1]))
    resources = observation.get("resources", [])
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    targets = []
    for r in resources:
        if r is None or len(r) != 2:
            continue
        tx, ty = r
        if (tx, ty) in obs:
            continue
        if (tx, ty) != (sx, sy):
            targets.append((tx, ty))
    if not targets:
        # No visible resources: try to move toward opponent if close to reduce denial impact, else hold.
        if dist(sx, sy, ox, oy) <= 2:
            tx, ty = ox, oy
        else:
            return [0, 0]
        targets = [(tx, ty)]

    best_move = (0, 0)
    bestv = None
    # Choose target that we are relatively closer to than opponent, then take best step toward it.
    for tx, ty in targets:
        myd = dist(sx, sy, tx, ty)
        opd = dist(ox, oy, tx, ty)
        target_value = (opd - myd) * 20 - myd  # prefer resources we can reach first
        # If we're already on a resource, just move with minimal disruption (prefer staying).
        if (sx, sy) == (tx, ty):
            target_value += 50
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            newd = dist(nx, ny, tx, ty)
            v = target_value + (myd - newd) * 10
            # avoid letting opponent land on same immediate step resource if we can deny by not moving onto it
            if (nx, ny) == (ox, oy):
                v -= 8
            if bestv is None or v > bestv:
                bestv = v
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]