def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))
    res_set = set(res)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18

    # Prefer moving toward nearest resource, while not getting too close to opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            # If engine would block us anyway, treat as very bad.
            continue

        if res:
            dres = min(cheb(nx, ny, rx, ry) for rx, ry in res)
        else:
            # No resources visible: head away from opponent toward our far corner.
            dres = 0

        dop = cheb(nx, ny, ox, oy)
        collected = 1 if (nx, ny) in res_set else 0

        # Utility: maximize collection chance and reduce resource distance; keep some distance from opponent.
        val = (1000 * collected) + (-10 * dres) + (0.25 * dop)

        # Deterministic tie-break: fixed order moves list, so only replace on strict improvement.
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]