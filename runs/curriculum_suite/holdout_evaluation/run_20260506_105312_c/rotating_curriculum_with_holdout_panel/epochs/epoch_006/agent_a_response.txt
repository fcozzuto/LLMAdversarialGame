def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        moved = 1 if (dx != 0 or dy != 0) else 0
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)

            cur_myd = cheb(sx, sy, rx, ry)
            if opd <= 1 and myd > opd:
                continue  # likely denied/stealable soon

            rel = opd - myd  # positive means we are closer than opponent
            progress = cur_myd - myd
            if myd == 0:
                val += 10000  # immediate take
            else:
                val += rel * 80 + progress * 25 - myd * 2

            # small nudge to prefer nearer targets overall
            val -= (opd <= 1) * myd * 3

        val += moved * 3
        if val > best_val:
            best_val = val
            best = (dx, dy)

    bx, by = best
    return [int(bx), int(by)]