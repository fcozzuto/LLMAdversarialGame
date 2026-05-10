def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", None) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", None) or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_sc = -10**18
    rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        sc = 0
        if resources:
            my_best = 10**9
            for rx, ry in resources:
                d_my = abs(nx - rx) + abs(ny - ry)
                d_op = abs(ox - rx) + abs(oy - ry)
                my_best = min(my_best, d_my)

                # Prefer resources where we can arrive no later than opponent.
                if d_my <= d_op:
                    # encourage closer grabs; slightly discourage huge opponent gap risk
                    sc += (rem + 1) * (120 - 15 * d_my) + (d_op - d_my)
                else:
                    # still allow when good, but heavily penalize being behind
                    sc += - (rem + 1) * (30 + 20 * (d_my - d_op)) - 2 * d_my

            # Also reward reducing our nearest-resource distance and moving away from opponent
            sc += 40 * (50 - my_best) + 6 * (abs(nx - ox) + abs(ny - oy))
        else:
            # No visible resources: move to increase distance from opponent and towards center-ish.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            sc += 2 * (abs(nx - ox) + abs(ny - oy))
            sc += - (abs(nx - cx) + abs(ny - cy))

        if sc > best_sc:
            best_sc = sc
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]