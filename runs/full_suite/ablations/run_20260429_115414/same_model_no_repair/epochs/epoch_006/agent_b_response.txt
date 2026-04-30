def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Predict opponent greedily toward the resource that maximizes its advantage over us.
    def best_adv_from(px, py, qx, qy):
        best = None
        for rx, ry in resources:
            adv = cheb(px, py, rx, ry) - cheb(qx, qy, rx, ry)  # lower for better target for (qx,qy)
            if best is None or adv < best[0]:
                best = (adv, rx, ry)
        return best  # (adv, rx, ry) or None

    opp_pred = best_adv_from(ox, oy, sx, sy) if resources else None
    target_opp = (opp_pred[1], opp_pred[2]) if opp_pred else None

    def free_neighbors_count(px, py):
        c = 0
        for ddx, ddy in dirs:
            nx, ny = px + ddx, py + ddy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                c += 1
        return c

    def move_value(nx, ny):
        if resources:
            # Choose the resource where we have maximum advantage (opponent distance - our distance).
            best_adv = -10**9
            best_res = None
            for rx, ry in resources:
                adv = cheb(ox, oy, rx, ry) - cheb(nx, ny, rx, ry)
                if adv > best_adv:
                    best_adv = adv
                    best_res = (rx, ry)
            # If opponent likely targets a specific resource, discourage letting them gain more.
            opp_pen = 0
            if target_opp is not None and best_res is not None:
                rx, ry = target_opp
                before = cheb(ox, oy, rx, ry) - cheb(sx, sy, rx, ry)
                after = cheb(ox, oy, rx, ry) - cheb(nx, ny, rx, ry)
                if after > before:
                    opp_pen = 0.75 * (after - before)
            # Prefer moves that keep options open.
            opt = free_neighbors_count(nx, ny)
            return 10.0 * best_adv + 0.8 * opt - opp_pen
        # No resources: move toward a corner that opp is not in (center-ish escape).
        tx, ty = (w - 1 if (sx + sy) < (ox + oy) else 0), (h - 1 if (sx + sy) < (ox + oy) else 0)
        return -cheb(nx, ny, tx, ty) + 0.5 * free_neighbors_count(nx, ny)

    best = None
    for dx, dy, nx, ny in moves:
        v =