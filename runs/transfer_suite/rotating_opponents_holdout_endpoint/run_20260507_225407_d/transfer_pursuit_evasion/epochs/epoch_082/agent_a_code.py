def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles or not inb(x, y)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    role = (observation.get("self_role") or "").lower()
    self_is_evader = ("evad" in role) or ("escape" in role) or ("runner" in role) or ("coward" in role)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = corners[0]
    best_far = -1
    for cx, cy in corners:
        d = cheb(cx, cy, ox, oy)
        if d > best_far:
            best_far = d
            far_corner = (cx, cy)

    best_move = (0, 0)
    if self_is_evader:
        best_key = None
        tx, ty = far_corner
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            dist = cheb(nx, ny, ox, oy)
            toward = cheb(nx, ny, tx, ty)  # smaller is better
            score = (-dist, toward, man(nx, ny, ox, oy), dx, dy)  # lexicographic
            if best_key is None or score < best_key:
                best_key = score
                best_move = (dx, dy)
    else:
        best_key = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            dist = cheb(nx, ny, ox, oy)
            m = man(nx, ny, ox, oy)
            # "wall runner" counter: prefer moves that keep reducing distance, tie-break by direction alignment
            align = (1 if nx > sx else (-1 if nx < sx else 0)) * (1 if ox > sx else (-1 if ox < sx else 0)) + \
                    (1 if ny > sy else (-1 if ny < sy else 0)) * (1 if oy > sy else (-1 if oy < sy else 0))
            score = (dist, m, -align, dx, dy)  # smaller is better; align higher is better via -align
            if best_key is None or score < best_key:
                best_key = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]