def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = observation.get("obstacles") or []
    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []

    us = {(p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2}
    ob = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}
    selfset = {(p[0], p[1]) for p in self_terr if isinstance(p, (list, tuple)) and len(p) >= 2}
    oppset = {(p[0], p[1]) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_to_opp(x, y):
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)):
            if (x + dx, y + dy) in oppset:
                return True
        return False

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidate_targets = list(us) if us else []
    if not candidate_targets:
        # chase opponent frontier-adjacent cells if no unclaimed
        for (x, y) in oppset:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)):
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in ob and (nx, ny) not in selfset:
                    candidate_targets.append((nx, ny))
        if not candidate_targets:
            candidate_targets = [(ox, oy)]

    best = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in ob:
            continue

        # Base preference: proximity to best target
        dist_best = 10**9
        for tx, ty in candidate_targets:
            d = man(nx, ny, tx, ty)
            if d < dist_best:
                dist_best = d

        val = -dist_best
        if (nx, ny) in us:
            val += 6
        if (nx, ny) in oppset:
            val += 10  # capture by flipping on entry
        if (nx, ny) in selfset:
            val += 1
        if adj_to_opp(nx, ny):
            val += 2  # edge pressure

        # avoid being stuck: prefer changing position unless equivalent
        if (dx, dy) != (0, 0):
            val += 0.1

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]