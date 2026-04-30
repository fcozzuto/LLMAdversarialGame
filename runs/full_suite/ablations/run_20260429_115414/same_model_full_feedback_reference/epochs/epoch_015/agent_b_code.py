def choose_move(observation):
    W = int(observation.get("grid_width", 8))
    H = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def best_target():
        if not res:
            return None
        best = None
        bestv = -10**18
        for rx, ry in res:
            if (rx, ry) in obs:
                continue
            dme = cheb(sx, sy, rx, ry)
            dob = cheb(ox, oy, rx, ry)
            v = (dob - dme) * 100 - dme
            if v > bestv or (v == bestv and (rx < best[0] or (rx == best[0] and ry < best[1]))):
                bestv = v
                best = (rx, ry)
        return best

    target = best_target()
    if target is None:
        # No resources: drift away from opponent, avoid obstacles
        best = (sx, sy)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obs:
                continue
            v = cheb(nx, ny, ox, oy)  # maximize distance
            if v > bestv or (v == bestv and (nx < best[0] or (nx == best[0] and ny < best[1]))):
                bestv = v
                best = (nx, ny)
        return [best[0] - sx, best[1] - sy]

    tx, ty = target
    best = (sx, sy)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obs:
            continue
        dme = cheb(nx, ny, tx, ty)
        dob = cheb(nx, ny, ox, oy)
        v = -dme * 50 + dob - (1 if (nx, ny) == (ox, oy) else 0)
        if v > bestv or (v == bestv and (nx < best[0] or (nx == best[0] and ny < best[1]))):
            bestv = v
            best = (nx, ny)

    return [best[0] - sx, best[1] - sy]