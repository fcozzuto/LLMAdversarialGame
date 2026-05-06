def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        my_best = -10**9
        deny_best = -10**9
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) in obs:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)

            # Prefer resources we can reach no later than opponent; otherwise deny by increasing their lead.
            beat = od - sd  # positive if we are closer/equal
            if beat >= 0:
                # Encourage fast access; also slightly prefer mid-grid to reduce corner trap.
                val = beat * 30 - sd * 3 - (abs(rx - (w // 2)) + abs(ry - (h // 2))) // 4
                if val > my_best:
                    my_best = val
            else:
                # We can't beat this resource now: try to worsen opponent's situation by moving closer to it.
                # Resource_denier-ish: minimize (od - sd) negativity and/or maximize distance-to-them.
                val = (-beat) * 5 - sd + 2  # lower sd helps deny by contesting approach
                if val > deny_best:
                    deny_best = val

        # If we have a beating option, prioritize it strongly; else fall back to denying/contesting.
        if my_best == -10**9 and deny_best == -10**9:
            # No resources considered; drift toward center while staying deterministic.
            cx, cy = w // 2, h // 2
            val = -man(nx, ny, cx, cy)
        else:
            val = my_best * 10 + deny_best

        # Deterministic tie-breaker: prefer smaller |dx|+|dy| then lexicographic.
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            cur_cost = abs(dx) + abs(dy)
            best_dx, best_dy = best_move
            best_cost = abs(best_dx) + abs(best_dy)
            if cur_cost < best_cost or (cur_cost == best_cost and (dx, dy) < (best_dx, best_dy)):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]