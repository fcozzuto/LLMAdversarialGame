def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    px, py = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = set(map(tuple, observation.get("resources") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    my_terr = set(map(tuple, observation.get("self_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def nearest_dist(x, y, cells):
        if not cells:
            return 10**9
        best = 10**9
        for cx, cy in cells:
            d = man(x, y, cx, cy)
            if d < best:
                best = d
                if best == 0:
                    return 0
        return best

    target_cells = resources if resources else (unclaimed if unclaimed else (opp_terr if opp_terr else set()))
    if not target_cells:
        target_cells = {(px, py)}

    best_dir = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in resources:
            score += 1000
        if (nx, ny) in unclaimed:
            score += 40
        if (nx, ny) in opp_terr:
            score += 120

        score += -nearest_dist(nx, ny, target_cells)
        score += 5 if (nx, ny) in my_terr else 0
        score += -2 * man(nx, ny, px, py)

        if score > best_score:
            best_score = score
            best_dir = (dx, dy)

    return [best_dir[0], best_dir[1]]