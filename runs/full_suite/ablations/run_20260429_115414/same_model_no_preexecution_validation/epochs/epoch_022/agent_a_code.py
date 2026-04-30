def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def obs_pen(x, y):
        if not obs:
            return 0.0
        md = 99
        for px, py in obs:
            d = cheb(x, y, px, py)
            if d < md:
                md = d
                if md <= 1:
                    break
        if md <= 1:
            return 4.0
        if md == 2:
            return 1.3
        return 0.0

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d0o = cheb(nx, ny, ox, oy)
        best = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < best:
                best = d
        if resources:
            want = best
        else:
            want = 0
        score = want + 0.55 * obs_pen(nx, ny) - 0.06 * d0o
        moves.append((score, -d0o, nx, ny, dx, dy))

    if not moves:
        return [0, 0]

    moves.sort(key=lambda t: (t[0], t[1], t[2], t[3], t[4], t[5]))
    return [int(moves[0][4]), int(moves[0][5])]