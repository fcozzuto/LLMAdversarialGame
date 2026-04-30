def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    x, y = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            ex, ey = int(o[0]), int(o[1])
            if inb(ex, ey):
                obstacles.add((ex, ey))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (None, -10**18)

    # Target heuristic: pick resource maximizing (opp_dist - self_dist)
    # with a tie-breaker toward closer overall.
    def target_for(px, py):
        best_r = resources[0]
        bd = md(px, py, best_r[0], best_r[1])
        bo = md(px, py, ox, oy)
        bgain = md(ox, oy, best_r[0], best_r[1]) - bd
        for rx, ry in resources[1:]:
            d = md(px, py, rx, ry)
            gain = md(ox, oy, rx, ry) - d
            if gain > bgain or (gain == bgain and (d < bd or (d == bd and d - bo > 0))):
                best_r = (rx, ry)
                bd, bgain = d, gain
        return best_r

    tx, ty = target_for(x, y)

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = x, y
        # If we stayed because invalid, still score consistently.
        sd = md(nx, ny, tx, ty)
        od = md(nx, ny, ox, oy)
        # Softly avoid letting opponent get closer to the same target.
        opp_sd = md(ox, oy, tx, ty)
        # Also add bias to reduce distance to the globally best resource.
        tx2, ty2 = target_for(nx, ny)
        sd2 = md(nx, ny, tx2, ty2)
        score = 10_000 - 100*sd - 10*sd2 + 2*od
        if md(ox, oy, nx, ny) <= 1 and (nx, ny) != (x, y):
            score -= 200  # discourage risky adjacent encounters
        if opp_sd - sd < 0:
            score += 50  # we are moving closer than opponent is
        if score > best[1]:
            best = ((dx, dy), score)

    dx, dy = best[0]
    return [int(dx), int(dy)]