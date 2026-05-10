def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))

    if not resources:
        cx, cy = w // 2, h // 2
        best = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            d = dist8(nx, ny, cx, cy)
            cand = (d, 0 if dx == 0 and dy == 0 else 1, -dist8(nx, ny, ox, oy))
            if cand < best:
                best = cand
        return [best[1] if len(best) > 1 else 0, best[2] if len(best) > 2 else 0]

    low_turns = observation.get("turns_remaining", 0) <= 8
    best_target = None
    best_adv = -10**18

    for rx, ry in resources:
        md = dist8(sx, sy, rx, ry)
        od = dist8(ox, oy, rx, ry)
        # Advantage: we prefer resources we can reach sooner; secondarily prefer farther from opponent.
        adv = (od - md)
        # Small tie-break to reduce oscillations: slightly prefer closer resources when close to end.
        adv -= 0.001 * md if not low_turns else 0.01 * md
        if adv > best_adv:
            best_adv = adv
            best_target = (rx, ry)

    tx, ty = best_target
    best_move = None
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        md2 = dist8(nx, ny, tx, ty)
        # Prefer reducing our distance; among ties, prefer maintaining/improving advantage.
        od2 = dist8(ox, oy, tx, ty)
        adv2 = od2 - md2
        # Deterministic tie-break: prefer non-stay moves with smaller (nx,ny) lex order.
        key = (md2, -adv2, 0 if (dx == 0 and dy == 0) else 1, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]