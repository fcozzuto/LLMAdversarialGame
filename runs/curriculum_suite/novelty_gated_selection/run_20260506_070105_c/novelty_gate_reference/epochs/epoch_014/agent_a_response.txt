def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y):
                res.append((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not res:
        mx, my = w // 2, h // 2
        dx = 0 if sx == mx else (1 if mx > sx else -1)
        dy = 0 if sy == my else (1 if my > sy else -1)
        return [dx, dy]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def score_resource(rx, ry):
        myd = md(sx, sy, rx, ry)
        opd = md(ox, oy, rx, ry)
        # Prefer resources we can reach first; also avoid those opponent is much closer to.
        return (opd - myd) * 0.7 - myd * 0.2

    target = res[0]
    bestv = score_resource(target[0], target[1])
    for rx, ry in res[1:]:
        v = score_resource(rx, ry)
        if v > bestv:
            bestv = v
            target = (rx, ry)

    # If we're very close to target, also consider opponent distance to reduce contest losses.
    tx, ty = target
    resset = set(res)
    best = None
    best_val = -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        base = 0
        if (nx, ny) in resset:
            base += 1000
        d_to_t = md(nx, ny, tx, ty)
        d_to_o = md(nx, ny, ox, oy)
        # Choose move that decreases distance to target, but keeps distance from opponent.
        val = base + (200 - d_to_t * 10) + d_to_o * 2
        # Small deterministic preference: when equal, prefer staying closer to target direction.
        if best is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]