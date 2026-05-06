def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        bestv = None
        for dx, dy, nx, ny in moves:
            v = (man(nx, ny, tx, ty), man(nx, ny, ox, oy))
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Estimate opponent target as nearest remaining resource to opponent
    opp_target = min(resources, key=lambda r: man(ox, oy, r[0], r[1]))
    otx, oty = opp_target

    def cell_value(x, y):
        sd = man(x, y, otx, oty)
        # primary: deny opponent by moving toward the opponent's nearest resource
        # secondary: race on any resource (prefer cells that make us closer than opponent)
        race_best = -10**9
        for rx, ry in resources:
            self_d = man(x, y, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            race_best = max(race_best, (opp_d - self_d))
        # small tie-break: prefer being closer to any resource we can win
        close_best = min(resources, key=lambda r: man(x, y, r[0], r[1]))
        close_d = man(x, y, close_best[0], close_best[1])
        return (race_best, -sd, -close_d)

    best = (0, 0)
    bestv = None
    for dx, dy, nx, ny in moves:
        v = cell_value(nx, ny)
        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)

    # If the best move is staying still, try to break ties by also winning a resource race
    if best == (0, 0):
        best2v = None
        best2 = best
        for dx, dy, nx, ny in moves:
            if dx == 0 and dy == 0:
                continue
            v = cell_value(nx, ny)
            if best2v is None or v > best2v:
                best2v = v
                best2 = (dx, dy)
        return [best2[0], best2[1]]

    return [best[0], best[1]]