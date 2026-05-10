def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((int(o[0]), int(o[1])))

    role = (observation.get("self_role", "") or "").lower()
    self_evader = ("evad" in role) or ("runner" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def corner_score(nx, ny):
        far_corner = corners[0]
        far_d = cheb(nx, ny, far_corner[0], far_corner[1])
        for c in corners[1:]:
            d = cheb(nx, ny, c[0], c[1])
            if d > far_d:
                far_d = d
                far_corner = c
        near_corner = corners[0]
        near_d = cheb(nx, ny, near_corner[0], near_corner[1])
        for c in corners[1:]:
            d = cheb(nx, ny, c[0], c[1])
            if d < near_d:
                near_d = d
                near_corner = c
        return far_d - near_d

    best = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        cs = corner_score(nx, ny)
        if self_evader:
            val = (d, cs)  # maximize distance, then prefer corner pressure
        else:
            val = (-d, cs)  # minimize distance, then prefer corner pressure
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]