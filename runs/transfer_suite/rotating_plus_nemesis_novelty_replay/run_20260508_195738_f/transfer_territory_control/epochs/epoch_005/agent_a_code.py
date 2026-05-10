def choose_move(observation):
    x, y = observation.get("self_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    opp_cells = set(tuple(c) for c in (observation.get("opponent_territory", []) or []))
    unclaimed = set(tuple(c) for c in (observation.get("unclaimed_cells", []) or []))
    self_cells = set(tuple(c) for c in (observation.get("self_territory", []) or []))
    obstacles = set(tuple(c) for c in (observation.get("obstacles", []) or []))
    ox, oy = observation.get("opponent_position", (0, 0))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If opponent is very close to our vicinity, switch to defensive maximization
    adj_opp = False
    for dx0 in (-1, 0, 1):
        for dy0 in (-1, 0, 1):
            if dx0 == 0 and dy0 == 0:
                continue
            nx0, ny0 = x + dx0, y + dy0
            if inb(nx0, ny0) and (nx0, ny0) in opp_cells:
                adj_opp = True
                break
        if adj_opp:
            break

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_s = -10**18
    best = (0, 0)

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d_center = cheb(nx, ny, cx, cy)
        d_opp = cheb(nx, ny, ox, oy)
        is_un = (nx, ny) in unclaimed
        is_self = (nx, ny) in self_cells
        is_opp = (nx, ny) in opp_cells

        if adj_opp:
            # Defense: avoid flipping into opponent; maximize separation
            s = 3.0 * d_opp + (1.0 if is_self else 0.0) - (2.5 if is_opp else 0.0) - (1.0 if is_un else 0.0) - 0.2 * d_center
        else:
            # Offense: expand toward center/unclaimed while keeping away from opponent territory
            s = 0.9 * d_center * (-1.0) + (0.8 if is_un else 0.0) + (0.2 if is_self else 0.0) - (1.2 if is_opp else 0.0) - 0.25 * d_opp

        if s > best_s or (s == best_s and (dx, dy) < best):
            best_s = s
            best = (dx, dy)

    return [int(best[0]), int(best[1])]