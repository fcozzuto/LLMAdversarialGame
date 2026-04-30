def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def boundary_pen(x, y):
        p = 0
        if x == 0 or x == w - 1: p += 2
        if y == 0 or y == h - 1: p += 2
        return p

    def adj_obst_pen(x, y):
        p = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                if (x + ddx, y + ddy) in obstacles:
                    p += 1
        return p

    if not resources:
        # Drift toward center while avoiding obstacles.
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        # Target the resource where we have the biggest distance advantage, tie-break by closeness to opponent.
        best = None
        for tx, ty in resources:
            sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            key = (od - sd, -sd, tx, ty)  # maximize (od-sd), then prefer closer to us, then deterministic
            if best is None or key > best[0]:
                best = (key, tx, ty)
        tx, ty = best[1], best[2]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Make progress to target; if we can take it earlier than opponent, prefer that strongly.
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        prog = od - sd
        # Avoid getting trapped near obstacles/boundaries.
        score = prog * 10 - sd - boundary_pen(nx, ny) * 2 - adj_obst_pen(nx, ny)
        # Prefer staying if it's already good, but ensure deterministic ordering.
        score += (0 if (dx, dy) != (0, 0) else 1)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]