def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    bestv = -10**18

    if resources:
        rx, ry = None, None
        md = 10**18
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                d = cd(x, y, r[0], r[1])
                if d < md:
                    md = d
                    rx, ry = r[0], r[1]
    else:
        rx, ry = w // 2, h // 2

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_target = cd(nx, ny, rx, ry)
        d_opp = cd(nx, ny, ox, oy)
        score = -(d_target * 10) + d_opp
        if resources:
            d_home = cd(nx, ny, x, y)
            score -= d_home * 0.1
        if score > bestv:
            bestv = score
            best = (dx, dy)

    return [best[0], best[1]]