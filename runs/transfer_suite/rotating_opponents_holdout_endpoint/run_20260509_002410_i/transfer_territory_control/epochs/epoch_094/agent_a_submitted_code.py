def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (sx, sy)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = observation.get("resources") or []
    res = set()
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    un_set = set()
    for p in unclaimed:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                un_set.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    center = (w // 2, h // 2)

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        score = 0
        if (nx, ny) in res:
            score += 10000
        if (nx, ny) in un_set:
            score += 2500
        if res:
            md = 10**9
            for rx, ry in res:
                d = man(nx, ny, rx, ry)
                if d < md:
                    md = d
            score += 400 - 20 * md
        else:
            score += -man(nx, ny, center[0], center[1])
        score += -30 * man(nx, ny, ox, oy)
        if score > best[0]:
            best = (score, dx, dy)
        elif score == best[0]:
            if dx, dy < (best[1], best[2]):
                best = (score, dx, dy)

    return [int(best[1]), int(best[2])]