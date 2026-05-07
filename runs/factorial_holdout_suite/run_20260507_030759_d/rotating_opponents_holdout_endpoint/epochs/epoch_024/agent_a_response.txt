def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        return [0, 0]

    # Pick the resource where we are most likely to arrive first (opponent farther than us)
    best_r = None
    best_adv = None
    best_sd = None
    for r in resources:
        if not isinstance(r, (list, tuple)) or len(r) < 2:
            continue
        rx, ry = r[0], r[1]
        if not inb(rx, ry):
            continue
        sd = md((sx, sy), (rx, ry))
        od = md((ox, oy), (rx, ry))
        adv = od - sd
        if best_r is None or adv > best_adv or (adv == best_adv and sd < best_sd):
            best_r, best_adv, best_sd = (rx, ry), adv, sd

    if best_r is None:
        return [0, 0]
    tx, ty = best_r

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue
        sd2 = md((nx, ny), (tx, ty))
        od2 = md((ox, oy), (tx, ty))
        adv2 = od2 - sd2
        # Prefer: higher advantage, then closer, then move that reduces distance most to target.
        moves.append((adv2, -sd2, abs(nx - tx) + abs(ny - ty), [dx, dy]))

    # If all legal moves are blocked (unlikely), allow staying unless blocked
    if not moves:
        if (sx, sy) in obs_set:
            for dx, dy in deltas:
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny):
                    return [dx, dy]
            return [0, 0]
        return [0, 0]

    moves.sort(reverse=True)
    return moves[0][3]