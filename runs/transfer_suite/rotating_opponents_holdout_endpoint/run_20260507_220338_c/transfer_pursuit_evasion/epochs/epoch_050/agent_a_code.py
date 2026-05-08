def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role_s = str(observation.get("self_role") or "").lower()
    is_evader = any(k in role_s for k in ("evad", "run", "away", "escape", "runner"))
    if not is_evader:
        is_evader = True  # default to evade if role unclear

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x, y):
        dx = abs(ox - x)
        dy = abs(oy - y)
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # When evading, bias toward being in the corner farthest from opponent; when pursuing, toward nearest corner to opponent.
    corner_target = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    tx, ty = corner_target

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_dxdy = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in blocked:
            continue

        dist = cheb(nx, ny)
        corner_dist = abs(nx - tx) + abs(ny - ty)
        if is_evader:
            score = dist * 10.0 - corner_dist * 0.01
        else:
            score = -dist * 10.0 + corner_dist * 0.01  # pursue by reducing distance

        # deterministic tie-break: prefer smaller dx,dy lexicographically after score
        if best_score is None or (score > best_score) or (score == best_score and (dx, dy) < best_dxdy):
            best_score = score
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]