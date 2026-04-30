def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles or not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Order resources by a stable key to keep determinism.
    resources.sort(key=lambda r: (r[0] * 31 + r[1] * 17))

    # Focus on the closest few resources to reduce noise.
    res2 = []
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        res2.append((d, rx, ry))
    res2.sort(key=lambda t: (t[0], t[1], t[2]))
    focus = res2[:min(6, len(res2))]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        val = 0
        # Immediate resource contest evaluation.
        for _, rx, ry in focus:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # If we are closer, gain; if opponent is closer, penalize (deny).
            diff = opd - myd
            if diff >= 0:
                val += 90 * diff - 3 * myd
            else:
                val += 55 * diff - 2 * opd

            # Small tie-break for picking a resource we can actually step toward.
            step_dir = (1 if rx > nx else (-1 if rx < nx else 0), 1 if ry > ny else (-1 if ry < ny else 0))
            if step_dir == (dx, dy):
                val += 2

        # Encourage not drifting away from center once resources diminish.
        rem = int(observation.get("remaining_resource_count") or len(resources))
        if rem <= 5:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            dist_center = abs(nx - cx) + abs(ny - cy)
            val -= int(dist_center * 2)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]