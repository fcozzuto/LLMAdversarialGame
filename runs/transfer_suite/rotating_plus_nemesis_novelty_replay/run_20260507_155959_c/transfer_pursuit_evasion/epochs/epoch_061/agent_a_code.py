def choose_move(observation):
    w = int(observation.get("grid_width") or 0) or 8
    h = int(observation.get("grid_height") or 0) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        try:
            x, y = r
            res.append((int(x), int(y)))
        except Exception:
            pass
    if not res and observation.get("remaining_resource_count", 0):
        res = []

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    nearest_res = None
    if res:
        nearest_res = min(res, key=lambda p: man(sx, sy, p[0], p[1]))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d_opp = man(nx, ny, ox, oy)
        if nearest_res:
            d_res = man(nx, ny, nearest_res[0], nearest_res[1])
            d_res_now = man(sx, sy, nearest_res[0], nearest_res[1])
            approach = d_res_now - d_res
            score = 3 * approach + d_opp * 0.01
        else:
            score = d_opp

        # Deterministic tie-break: prefer smaller (dx,dy) lexicographically
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]