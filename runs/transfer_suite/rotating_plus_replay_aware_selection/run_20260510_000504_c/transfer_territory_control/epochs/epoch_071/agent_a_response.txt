def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    resources = observation.get("resources") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def mdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx = (w - 1) // 2
    cy = (h - 1) // 2

    if resources:
        tx, ty = resources[0]
    else:
        target = None
        best = None

        # 1) Counterclaim pressure: unclaimed cells adjacent to opponent territory
        if opp_terr:
            for (ox, oy) in opp_terr:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = ox + dx, oy + dy
                        if inb(nx, ny) and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                            score = (mdist(sx, sy, nx, ny), mdist(cx, cy, nx, ny))
                            if best is None or score < best:
                                best = score
                                target = (nx, ny)
        # 2) Expand our frontier: unclaimed adjacent to our territory
        if target is None and self_terr:
            for (x, y) in self_terr:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if inb(nx, ny) and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                            score = (mdist(sx, sy, nx, ny), abs(nx - cx) + abs(ny - cy))
                            if best is None or score < best:
                                best = score
                                target = (nx, ny)

        # 3) Fallback: any unclaimed cell, biased toward center
        if target is None:
            for (nx, ny) in unclaimed:
                if (nx, ny) in obstacles:
                    continue
                score = (mdist(sx, sy, nx, ny), abs(nx - cx) + abs(ny - cy))
                if best is None or score < best:
                    best = score
                    target = (nx, ny)

        tx, ty = (sx, sy) if target is None else target

    # Greedily pick legal move that minimizes distance to target, with a tie-breaker toward center
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = (mdist(nx, ny, tx, ty), abs(nx - cx) + abs(ny - cy))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]