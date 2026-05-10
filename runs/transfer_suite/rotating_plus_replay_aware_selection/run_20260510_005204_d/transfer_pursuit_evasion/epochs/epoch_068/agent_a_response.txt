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

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def near_obst(x, y):
        c = 0
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if (x + i, y + j) in blocked:
                    c += 1
        return c

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    opp_corner = max(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))
    opp_is_cornerish = cheb(ox, oy, opp_corner[0], opp_corner[1]) == 0

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            val = -10**9 if we_pursuer else -10**9
        else:
            dist = cheb(nx, ny, ox, oy)
            obst_pen = near_obst(nx, ny)
            # Evader: maximize distance, avoid obstacles; if opponent in corner, prefer moving along a "ring" (increase one axis while not decreasing the other too much).
            if we_evader:
                ring = 0
                if opp_is_cornerish:
                    tx, ty = opp_corner
                    # Perpendicular-ish bias: if opponent corner is in same general direction, try to move to increase the axis away from corner.
                    sx_dir = 1 if nx > sx else (-1 if nx < sx else 0)
                    sy_dir = 1 if ny > sy else (-1 if ny < sy else 0)
                    cx_dir = 1 if (nx - tx) > 0 else (-1 if (nx - tx) < 0 else 0)
                    cy_dir = 1 if (ny - ty) > 0 else (-1 if (ny - ty) < 0 else 0)
                    ring = (cx_dir * sx_dir) + (cy_dir * sy_dir)
                    # Also slightly reward increasing distance more than just changing position.
                    ring += (dist - cheb(sx, sy, ox, oy))
                val = dist * 10 - obst_pen * 2 + ring
            else:
                # Pursuer: minimize distance, avoid obstacles, and prefer moves that reduce distance most.
                val = -dist * 10 - obst_pen * 2
        if best_val is None or (we_evader and val > best_val) or (we_pursuer and val > best_val):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]