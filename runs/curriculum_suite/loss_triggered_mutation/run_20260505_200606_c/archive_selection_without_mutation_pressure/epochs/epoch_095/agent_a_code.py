def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            r = (p[0], p[1])
            if r not in obstacles:
                resources.append(r)
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_dx, best_dy = 0, 0
    best_val = -10**18

    adj_opp = max(abs(sx - ox), abs(sy - oy))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Intercept: prioritize resources where opponent is nearer (ds - do small/negative).
        v = 0
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # If opponent is closer (ds>do), we want to reduce the gap (make ds-do large negative).
            gap = ds - do
            v += (-gap) * 220 - ds
            if ds == 0:
                v += 10**7

        # Defensive shaping: discourage staying too adjacent to opponent's position.
        dmax = max(abs(nx - ox), abs(ny - oy))
        v -= (6 - dmax) * 40 if dmax < 6 else 0

        # Tie-breaker: prefer forward-ish towards center to fight sweep patterns.
        cx, cy = (w - 1) / 2, (h - 1) / 2
        v -= int((abs(nx - cx) + abs(ny - cy)) * 3)

        if v > best_val:
            best_val = v
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]