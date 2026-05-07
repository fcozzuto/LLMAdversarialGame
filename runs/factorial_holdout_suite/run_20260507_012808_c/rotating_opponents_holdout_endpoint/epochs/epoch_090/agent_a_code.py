def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = (0, 0)
    best_val = -10**18

    # Evaluate each move by the best resource "advantage" we can contest.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if resources:
            cur_best = -10**18
            for rx, ry in resources:
                sd = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                # Prefer resources where we arrive earlier; slight preference for closer overall.
                val = (od - sd) * 1000 - sd
                if val > cur_best:
                    cur_best = val
            # Also keep moving roughly away from opponent to reduce interference.
            opp = man(nx, ny, ox, oy)
            val2 = cur_best + opp * 2
        else:
            # No resources visible: move toward center, away from opponent a bit.
            val2 = -(man(nx, ny, cx, cy)) + man(nx, ny, ox, oy) * 0.5

        # Deterministic tie-breaker: lexicographic on (dx, dy) with higher val first.
        if val2 > best_val or (val2 == best_val and (dx, dy) < best_move):
            best_val = val2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]