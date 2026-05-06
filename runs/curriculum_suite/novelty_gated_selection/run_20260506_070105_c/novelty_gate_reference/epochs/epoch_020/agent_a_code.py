def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                blocked.add((int(x), int(y)))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    any_res = False
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        score = 0
        nearest_res_dist = None

        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = r[0], r[1]
            rx, ry = int(rx), int(ry)
            if not (0 <= rx < w and 0 <= ry < h) or (rx, ry) in blocked:
                continue
            any_res = True
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            nearest_res_dist = ds if nearest_res_dist is None else min(nearest_res_dist, ds)
            # Prefer moving toward resources we can reach sooner (or deny if not).
            if ds <= do:
                score += 1000 - 50 * ds
            else:
                score += -200 - 10 * (ds - do)

        if any_res:
            if nearest_res_dist is None:
                score -= 99999
            else:
                score -= nearest_res_dist  # keep moving toward closer resources
        else:
            # No resources: move toward center
            cx, cy = (w - 1) // 2, (h - 1) // 2
            score += -man(nx, ny, cx, cy)

        # Small deterministic bias: prefer not to move backward toward opponent
        score += -1 * (man(nx, ny, ox, oy) > man(sx, sy, ox, oy)) if (0 <= ox < w and 0 <= oy < h) else 0

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]