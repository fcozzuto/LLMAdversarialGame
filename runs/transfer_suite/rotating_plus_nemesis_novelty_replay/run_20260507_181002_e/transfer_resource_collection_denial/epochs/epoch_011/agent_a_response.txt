def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = observation.get("obstacles", [])
    obs = set()
    for p in obstacles:
        if p is not None and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    res = observation.get("resources", [])
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not res:
        cx, cy = w // 2, h // 2
        tx, ty = cx, cy
        best = (0, 0)
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            d = dist(nx, ny, tx, ty)
            if d < bestd:
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate: prefer resources we can get first; if likely contested, deny by minimizing opponent advantage.
        total = 0
        for r in res:
            if r is None or len(r) != 2:
                continue
            tx, ty = r
            if (tx, ty) in obs or (tx == nx and ty == ny):
                continue
            my = dist(nx, ny, tx, ty)
            opp = dist(ox, oy, tx, ty)
            # If opponent can beat us, we value it negatively; otherwise positively.
            # Also prefer far-from-opponent targets when contested.
            if my < opp:
                total += (opp - my + 1) * 2 - my * 0.2
            elif my == opp:
                total += (dist(ox, oy, tx, ty) * -0.05) + (my * -0.1)
            else:
                total += (my - opp) * -3 - dist(ox, oy, tx, ty) * 0.02

        # If we can immediately step onto a resource, take it.
        for r in res:
            if r is not None and len(r) == 2 and r[0] == nx and r[1] == ny:
                total += 1000
                break

        if total > best_val:
            best_val = total
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]