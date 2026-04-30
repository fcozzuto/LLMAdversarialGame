def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    if not resources:
        tx, ty = (w // 2, h // 2)
        best = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                d = dist((nx, ny), (tx, ty))
                if d < best[0] or (d == best[0] and (dx, dy) < (best[1], best[2])):
                    best = (d, dx, dy)
        return [int(best[1]), int(best[2])]

    # Evaluate each candidate move by the best "pickable" resource considering opponent threat.
    best_move = (10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_pos = (nx, ny)
        best_for_move = 10**18

        # Deterministic ordering helps tie-breaking
        for rx, ry in sorted(resources):
            res = (rx, ry)
            myd = dist(my_pos, res)
            opd = dist((ox, oy), res)

            # If opponent is much closer, heavily penalize; otherwise prefer quicker pickups.
            threat = 0
            if opd <= myd:
                # Make it near-unacceptable when opponent can arrive first or same time
                threat = (myd - opd) - 6  # negative or zero => penalty
            # Small bias to move toward resources while also discouraging staying away from best options.
            score = myd * 10 + threat * 20 + (rx + 3 * ry) * 0.001

            if score < best_for_move:
                best_for_move = score

        # Tie-break by lexicographic move preference (deterministic)
        if best_for_move < best_move[0] or (best_for_move == best_move[0] and (dx, dy) < (best_move[1], best_move[2])):
            best_move = (best_for_move, dx, dy)

    return [int(best_move[1]), int(best_move[2])]