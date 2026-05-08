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
    is_pursuer = ("purs" in role_s) or ("hunt" in role_s) or ("chase" in role_s)
    if not (is_evader or is_pursuer):
        is_evader = True

    target_corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_corner = max(target_corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x, y):
        dx = abs(ox - x)
        dy = abs(oy - y)
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    tx, ty = best_corner
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d = cheb(nx, ny)
        corner_dist = abs(nx - tx) + abs(ny - ty)
        # Prefer staying away from opponent as evader; prefer reducing distance as pursuer.
        val = d + (-0.02 * corner_dist if is_evader else 0.02 * corner_dist)
        if best is None:
            best, best_val = (dx, dy), val
        else:
            if is_evader:
                if val > best_val or (val == best_val and (dx, dy) < best):
                    best, best_val = (dx, dy), val
            else:
                if val < best_val or (val == best_val and (dx, dy) < best):
                    best, best_val = (dx, dy), val

    if best is None:
        return [0, 0]
    return [best[0], best[1]]