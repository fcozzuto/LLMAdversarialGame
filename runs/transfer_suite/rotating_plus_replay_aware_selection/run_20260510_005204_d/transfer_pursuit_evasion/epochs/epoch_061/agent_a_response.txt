def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    we_evader = ("evader" in role) or ("runner" in role)
    we_pursuer = not we_evader

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

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

    def near_obst(x, y):
        c = 0
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if (x + i, y + j) in blocked:
                    c += 1
        return c

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_dxdy = (0, 0)
    best_key = None

    # Corner tendency for evasion: if opponent seems in a corner, create lateral separation instead of pure distance.
    def corner_score(x, y):
        # higher means closer to a corner
        d1 = cheb(x, y, 0, 0)
        d2 = cheb(x, y, w - 1, 0)
        d3 = cheb(x, y, 0, h - 1)
        d4 = cheb(x, y, w - 1, h - 1)
        d = d1
        if d2 < d: d = d2
        if d3 < d: d = d3
        if d4 < d: d = d4
        return -d

    opp_corner_bias = corner_score(ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        dist = cheb(nx, ny, ox, oy)
        obst = near_obst(nx, ny)

        # Pursuer: reduce distance strongly, avoid obstacles, also prefer decreasing both axes when possible.
        # Evader: increase distance, avoid obstacles, and try to keep x or y offset to break straight pursuit.
        if we_pursuer:
            axis = abs(nx - ox) + abs(ny - oy)
            key = (dist, obst, axis, nx + ny, nx, ny)
            # min key
            if best_key is None or key < best_key:
                best_key = key
                best_dxdy = (dx, dy)
        else:
            dist_gain = dist
            xoff = abs(nx - ox)
            yoff = abs(ny - oy)
            # if opponent is near corner, prioritize lateral escape (maximize xoff or yoff rather than only cheb)
            lateral = xoff if xoff > yoff else yoff
            key = (-dist_gain, obst, -(lateral if opp_corner_bias >= -1 else (xoff + yoff)), -(nx + ny), -nx, -ny)
            if best_key is None or key < best_key:
                best_key = key
                best_dxdy = (dx, dy)

    dx, dy = best_dxdy
    return [int(dx), int(dy)]