def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("pursuer" in role) or (("pursuer" in opp_role) and ("evader" not in role))
    if ("evader" in role) and ("pursuer" not in role):
        pursuer = False

    moves = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def dist_to_center_infty(x, y):
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dx = abs(x - cx)
        dy = abs(y - cy)
        return dx if dx > dy else dy

    def farthest_corner_towards_away():
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = corners[0]
        bestd = -1
        for cx, cy in corners:
            d = cheb(cx, cy, ox, oy)
            if d > bestd:
                bestd = d
                best = (cx, cy)
        return best

    target_corner = farthest_corner_towards_away() if not pursuer else None

    best = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d = cheb(nx, ny, ox, oy)

        # extra terms to cope with wall-running: prefer routes that keep options open
        open_cnt = 0
        for adx, ady in moves:
            tx, ty = nx + adx, ny + ady
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                open_cnt += 1

        if pursuer:
            # chase while avoiding getting trapped in tight obstacle pockets
            # maximize: (-distance) and openness
            center_bias = -0.02 * dist_to_center_infty(nx, ny)
            val = (-d) + 0.06 * open_cnt + center_bias
            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)
        else:
            # evade: maximize distance, also bias toward a corner that pulls away
            tx, ty = target_corner
            corner_d = cheb(nx, ny, tx, ty)
            corner_adv = -0.015 * corner_d  # smaller corner_d is better (closer to chosen away-corner)
            val = d + 0.05 * open_cnt + corner_adv
            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)

    return [int(best[0]), int(best[1])]