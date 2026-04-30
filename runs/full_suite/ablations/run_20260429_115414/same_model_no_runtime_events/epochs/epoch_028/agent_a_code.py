def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cenx, ceny = (w - 1) / 2.0, (h - 1) / 2.0
    odists = {}
    for tx, ty in resources:
        odists[(tx, ty)] = cheb(ox, oy, tx, ty)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-(10**18), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        best_res = -(10**18)
        for tx, ty in resources:
            sdist = cheb(nx, ny, tx, ty)
            od = odists[(tx, ty)]
            lead = od - sdist  # positive => we arrive earlier
            center = abs(tx - cenx) + abs(ty - ceny)
            # Strong preference for winning a contested resource; otherwise maximize lead and efficiency.
            score = 0
            if lead > 0:
                score += 100000
            score += lead * 100 - sdist * 3 - center * 0.5
            # Slightly discourage moves that would get stuck behind an obstacle-adjacent corridor
            if (tx == nx or ty == ny):
                score += 1
            if score > best_res:
                best_res = score

        if best_res > best[0]:
            best = (best_res, dx, dy)

    return [int(best[1]), int(best[2])]