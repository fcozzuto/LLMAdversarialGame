def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    my_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    frontier = []
    if my_terr:
        for x, y in my_terr:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs and (nx, ny) not in my_terr:
                        frontier.append((x, y))
                        dx = dy = 2
                        break
                else:
                    continue
                break

    if not frontier:
        frontier = list(my_terr)[:1] if my_terr else [(sx, sy)]

    target_pool = []
    for c in unclaimed:
        target_pool.append((c[0], c[1], 5))
    for c in opp_terr:
        target_pool.append((c[0], c[1], 12))
    if not target_pool:
        tx, ty = (w - 1, h - 1) if (sx + sy) < (w - 1 + h - 1) else (0, 0)
        target_pool = [(tx, ty, 4)]

    best = None
    for tx, ty, base in target_pool:
        d = min(abs(tx - fx) + abs(ty - fy) for fx, fy in frontier)
        val = base - 0.15 * d
        if best is None or val > best[0] or (val == best[0] and (tx, ty) < (best[1], best[2])):
            best = (val, tx, ty)
    _, tx, ty = best

    def cell_value(x, y):
        if (x, y) in my_terr:
            return 2
        if (x, y) in opp_terr:
            return 10
        if (x, y) in unclaimed:
            return 6
        return 0

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        dist = abs(tx - nx) + abs(ty - ny)
        score = cell_value(nx, ny) - 0.25 * dist
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]