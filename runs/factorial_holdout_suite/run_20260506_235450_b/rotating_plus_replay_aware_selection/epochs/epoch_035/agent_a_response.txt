def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    best = (10**9, 10**9, 10**9, 0, 0)
    # Score tuple: (min advantage, min selfd, min oppd, lex dx, lex dy) for determinism
    for dx, dy, nx, ny in legal:
        cur_adv = 10**9
        cur_self = 10**9
        cur_opp = 10**9
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = sd - od
            if adv < cur_adv or (adv == cur_adv and (sd < cur_self or (sd == cur_self and od < cur_opp))):
                cur_adv, cur_self, cur_opp = adv, sd, od
        cand = (cur_adv, cur_self, cur_opp, dx, dy)
        if cand < best:
            best = cand
    return [int(best[3]), int(best[4])]