def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((int(o[0]), int(o[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role) or ("escape" in role) or ("escape" in (observation.get("environment_name", "") or "").lower())
    is_pursuer = not is_evader

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def mob(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                c += 1
        return c

    def obstacle_pressure(x, y):
        p = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
                p += 1
        return p

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        m = mob(nx, ny)
        op = obstacle_pressure(nx, ny)
        # Evader: maximize distance, keep mobility, avoid tight obstacle pressure
        if is_evader:
            val = d * 10.0 + m * 1.0 - op * 0.6
            # Extra determinism/anti-oscillation: prefer increasing distance first, then mobility
            if best_val is None or val > best_val + 1e-9:
                best_val = val
                best_move = (dx, dy)
            elif abs(val - best_val) <= 1e-9 and (d > cheb(sx, sy, ox, oy)):
                best_move = (dx, dy)
        else:
            # Pursuer: minimize distance, keep mobility, avoid obstacle pressure
            val = -d * 10.0 + m * 1.0 - op * 0.6
            if best_val is None or val > best_val + 1e-9:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]