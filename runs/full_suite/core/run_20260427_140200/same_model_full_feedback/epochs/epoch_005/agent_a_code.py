def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    rpos = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                rpos.append((x, y))

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
    cx, cy = (w - 1) // 2, (h - 1) // 2

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = int(sx + dx), int(sy + dy)
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Prefer approaching the nearest remaining resource.
        if rpos:
            dmin = 10**9
            for rx, ry in rpos:
                d = cheb(nx, ny, rx, ry)
                if d < dmin:
                    dmin = d
            res_term = -3.2 * dmin
        else:
            res_term = 0.0

        # Slightly prefer increasing distance from opponent (avoid being too close).
        oppd = cheb(nx, ny, int(ox), int(oy))
        opp_term = 0.8 * oppd

        # Keep near center to reduce travel and avoid edge trapping.
        cen_d = cheb(nx, ny, cx, cy)
        cen_term = -0.15 * cen_d

        # Mild obstacle awareness: penalize moves that have fewer free neighbors.
        free_n = 0
        for adx, ady in dirs:
            tx, ty = nx + adx, ny + ady
            if inb(tx, ty) and (tx, ty) not in obs:
                free_n += 1
        safe_term = 0.15 * free_n

        val = res_term + opp_term + cen_term + safe_term
        if val > best_val:
            best_val = val
            best_move = [int(dx), int(dy)]

    return best_move