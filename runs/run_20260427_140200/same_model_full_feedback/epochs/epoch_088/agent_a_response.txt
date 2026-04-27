def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        resources = [(w // 2, h // 2)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    # Determine a "target" resource: closest to us; deterministic tie by order.
    best_t = resources[0]
    best_td = 10**9
    for r in resources:
        d = cheb(sx, sy, r[0], r[1])
        if d < best_td:
            best_td = d
            best_t = r

    tx, ty = best_t

    # If opponent is closer to our target, add mild contest: prefer moves that increase their distance to it.
    opp_closer = cheb(ox, oy, tx, ty) < best_td

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_self_t = cheb(nx, ny, tx, ty)
        # Also consider overall nearest resource to avoid getting stuck if target disappears.
        d_self_near = 10**9
        for r in resources:
            dr = cheb(nx, ny, r[0], r[1])
            if dr < d_self_near:
                d_self_near = dr

        d_opp_t = cheb(ox, oy, tx, ty)
        d_opp_pos = cheb(nx, ny, ox, oy)

        # Value: go to resources, stay away from opponent unless contesting target.
        val = 0
        val += -2.4 * d_self_t
        val += -0.9 * d_self_near
        val += 0.35 * d_opp_pos
        if opp_closer:
            val += 1.2 * (d_opp_t - cheb(nx, ny, tx, ty))  # prefer progress toward target but not allowing easy steal by blocking path

        # Deterministic tie-break: first in deltas order.
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]