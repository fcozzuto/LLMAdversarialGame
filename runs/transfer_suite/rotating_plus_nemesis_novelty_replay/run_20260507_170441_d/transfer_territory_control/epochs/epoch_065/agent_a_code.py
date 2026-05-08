def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                res.append((x, y))
        except:
            pass

    def best_target():
        if res:
            return min(res, key=lambda r: abs(r[0] - sx) + abs(r[1] - sy))
        return (ox, oy)

    tx, ty = best_target()

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to_t = abs(nx - tx) + abs(ny - ty)
        d_to_o = abs(nx - ox) + abs(ny - oy)
        score = -d_to_t
        if (nx, ny) in res:
            score += 1000
        score += 0.01 * (d_to_o * -1)  # slight preference to reduce distance to opponent if no resources
        if dx == 0 and dy == 0:
            score -= 0.1
        if score > best_score:
            best_score = score
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best