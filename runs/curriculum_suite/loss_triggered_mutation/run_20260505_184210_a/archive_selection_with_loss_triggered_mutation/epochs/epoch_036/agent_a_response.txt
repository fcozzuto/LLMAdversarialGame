def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    def cheb_dist(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    # Score tries to create multiple "winning races" against opponent, not just nearest.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        for rx, ry in resources:
            sd = cheb_dist(nx, ny, rx, ry)
            od = cheb_dist(ox, oy, rx, ry)
            if sd == 0:
                val += 10000
            # Strongly prefer resources where we are strictly closer than opponent.
            # Chebyshev makes this consistent with 8-direction movement.
            diff = od - sd
            if diff > 0:
                val += 200 * diff - sd
            else:
                # If we can't win it, penalize proportionally to how close opponent is.
                val -= 2 * sd + (1 - diff) * 3 + (od == sd) * 5

        # Small tie-break: reduce distance to the best (currently most winnable) resource.
        # Deterministic and cheap.
        best_op = 10**9
        for rx, ry in resources:
            sd0 = cheb_dist(sx, sy, rx, ry)
            od0 = cheb_dist(ox, oy, rx, ry)
            if od0 - sd0 > 0:
                dd = sd0
                if dd < best_op:
                    best_op = dd
        if best_op == 10**9:
            best_op = min(cheb_dist(nx, ny, rx, ry) for rx, ry in resources)
        val -= best_op * 0.01

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]