def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy
    def obstacle_pen(x, y):
        if (x, y) in obstacles:
            return 10
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                if (x + dx, y + dy) in obstacles:
                    return 1
        return 0

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    best_target = None
    best_score = 10**18
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we're significantly closer to; otherwise prefer still-closable ones.
        score = sd - (0.6 if sd <= od else 0.0) + (2.2 if od + 1 < sd else 0.0)
        # Mild tie-break towards keeping distance from opponent (reduces being contested).
        score += 0.05 * cheb(sx, sy, ox, oy)
        if score < best_score:
            best_score = score
            best_target = (rx, ry)

    tx, ty = best_target
    best_move = (0, 0)
    best_val = -10**18
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue
        val = -cheb(nx, ny, tx, ty)
        val -= 0.8 * obstacle_pen(nx, ny)
        # If moving would let opponent get much closer to our target next, discourage slightly.
        od_next = cheb(ox, oy, tx, ty)  # opponent move unknown; use current as conservative.
        val += 0.02 * (od_next - cheb(nx, ny, tx, ty))
        # Deterministic tie-break: prefer moves with larger x then larger y, then stay last.
        if val > best_val or (val == best_val and (mx, my) > best_move):
            best_val = val
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]