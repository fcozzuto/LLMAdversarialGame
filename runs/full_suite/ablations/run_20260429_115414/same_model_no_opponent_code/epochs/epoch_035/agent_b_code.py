def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        # Fall back: move away from opponent while staying in-bounds
        deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        best = (0, 0); bestv = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = abs(nx - ox) if abs(nx - ox) > abs(ny - oy) else abs(ny - oy)
                if d > bestv:
                    bestv = d; best = (dx, dy)
        return [best[0], best[1]]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Choose a resource where we have the largest distance advantage over opponent
    best_target = resources[0]
    best_adv = -10**9
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd  # positive means we are closer (or opponent farther)
        # Mild tiebreak: prefer closer overall to reduce time-to-pick
        if adv > best_adv or (adv == best_adv and sd < cheb(sx, sy, best_target[0], best_target[1])):
            best_adv = adv
            best_target = (rx, ry)

    tx, ty = best_target
    curd = cheb(sx, sy, tx, ty)

    # Move one step toward target while avoiding obstacles and also considering opponent pressure
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        # value: reduce target distance, improve our advantage vs opponent, and avoid getting too close to opponent late
        my_adv = cheb(nx, ny, tx, ty)
        opp_adv = cheb(ox, oy, tx, ty)
        pressure = cheb(nx, ny, ox, oy)
        val = (curd - nd) * 1000 + (opp_adv - my_adv) * 10 + pressure
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]