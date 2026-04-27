def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    rpos = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            rpos.append((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    cx = (w - 1) // 2
    cy = (h - 1) // 2

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        if rpos:
            dmin = 10**9
            for rx, ry in rpos:
                d = cheb(nx, ny, rx, ry)
                if d < dmin: dmin = d
            oppd = cheb(nx, ny, ox, oy)
            score = -dmin * 1000 + oppd
        else:
            to_center = cheb(nx, ny, cx, cy)
            oppd = cheb(nx, ny, ox, oy)
            score = oppd * 1000 - to_center

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move