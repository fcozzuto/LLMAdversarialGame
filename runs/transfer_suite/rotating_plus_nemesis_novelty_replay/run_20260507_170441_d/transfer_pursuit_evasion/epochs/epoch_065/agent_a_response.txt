def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if free(nx, ny):
                c += 1
        return c

    role = (observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # pick a corner that maximizes distance to opponent (evader) or minimizes it (pursuer)
    best_corner = None
    best_corner_val = None
    for cx, cy in corners:
        if not free(cx, cy):
            continue
        v = cheb(cx, cy, ox, oy)
        if best_corner_val is None or (v > best_corner_val if is_evader else v < best_corner_val):
            best_corner_val = v
            best_corner = (cx, cy)
    if best_corner is None:
        best_corner = (sx, sy)

    tx, ty = best_corner

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_to_opp = cheb(nx, ny, ox, oy)
        d_to_corner = cheb(nx, ny, tx, ty)
        mob = mobility(nx, ny)
        # Score: pursuer minimize distance; evader maximize distance and corner progress with safety.
        if is_evader:
            score = (d_to_opp * 1000) + (-(mob) * 3) + (-(d_to_corner) * 1)
            better = best_score is None or score > best_score
        else:
            score = (-(d_to_opp) * 1000) + (mob * 3) + (-(d_to_corner) * 1)
            better = best_score is None or score > best_score
        if better:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]