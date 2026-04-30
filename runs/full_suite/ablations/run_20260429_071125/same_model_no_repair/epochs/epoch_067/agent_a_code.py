def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = []
    for p in (observation.get("resources") or []):
        x, y = p
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    center = ((w - 1) // 2, (h - 1) // 2)

    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy, nx, ny in legal:
            best_res_val = -10**18
            for rx, ry in resources:
                ourd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                adv = opd - ourd
                if ourd == 0:
                    res_val = 10**6 + adv * 1000
                else:
                    res_val = adv * 50 - ourd * 3 - opd * 0.5
                # small tie-breaks for stability
                res_val -= 0.1 * cheb(nx, ny, center[0], center[1])
                if res_val > best_res_val:
                    best_res_val = res_val
            # Encourage maintaining/creating separation when not committing to a resource
            sep = cheb(nx, ny, ox, oy)
            val = best_res_val + 0.15 * sep
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]
    else:
        # No visible resources: move toward center while not collapsing toward opponent
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy, nx, ny in legal:
            val = -cheb(nx, ny, center[0], center[1]) + 0.05 * cheb(nx, ny, ox, oy)
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]