def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    occ = {(p[0], p[1]) for p in obstacles}
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obstacle_pen(x, y):
        if (x, y) in occ:
            return 10**9
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in occ:
                    pen += 4 if (ax == 0 or ay == 0) else 3
        return pen

    def min_res_dist(x, y):
        best = 10**9
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < best:
                best = d
        return best

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in occ:
            continue

        dres = min_res_dist(nx, ny)
        dopp = cheb(nx, ny, ox, oy)

        # If the opponent is very close, avoid moving adjacent if possible
        threat_adj = 0
        if cheb(nx, ny, ox, oy) <= 1:
            threat_adj = 8
        if cheb(nx, ny, ox, oy) <= 0:
            threat_adj = 20

        val = (-1.6 * dres) + (0.35 * dopp) - obstacle_pen(nx, ny) - threat_adj
        # Small deterministic tie-breaker to keep motion stable
        val += 0.01 * (nx - ny)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]