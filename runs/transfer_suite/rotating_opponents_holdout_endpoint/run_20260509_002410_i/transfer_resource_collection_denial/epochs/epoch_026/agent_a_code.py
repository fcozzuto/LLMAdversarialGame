def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def mdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        tx, ty = w // 2, h // 2
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            v = -(mdist(nx, ny, tx, ty))
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # pick the resource where we are most likely to collect first
    best_r = None
    best_adv = -10**18
    for rx, ry in resources:
        sd = mdist(sx, sy, rx, ry)
        od = mdist(ox, oy, rx, ry)
        adv = od - sd
        if adv > best_adv or (adv == best_adv and (best_r is None or sd < mdist(sx, sy, best_r[0], best_r[1]))):
            best_adv = adv
            best_r = (rx, ry)

    rx, ry = best_r
    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        new_sd = mdist(nx, ny, rx, ry)
        new_adv = mdist(ox, oy, rx, ry) - new_sd
        # Encourage approaching chosen resource; also avoid falling behind badly
        v = new_adv * 10 - new_sd
        # Small tie-break toward moving in direction of target to reduce dithering
        v += -0.01 * mdist(nx, ny, rx, ry)
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best