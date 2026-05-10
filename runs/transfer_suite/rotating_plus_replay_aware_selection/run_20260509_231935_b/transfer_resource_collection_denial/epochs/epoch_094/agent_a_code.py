def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_raw = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obs_raw if p and len(p) >= 2}
    res = [(p[0], p[1]) for p in resources if p and len(p) >= 2]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def adj_obst(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    if not res:
        best = (-(10**9), 0, (0, 0))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            score = -cheb(nx, ny, ox, oy) - 2 * adj_obst(nx, ny)
            if score > best[0]:
                best = (score, cheb(nx, ny, ox, oy), (dx, dy))
        return [best[2][0], best[2][1]]

    best = (-(10**18), 0, (0, 0))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in obstacles:
            continue
        a = 0
        min_self = 10**9
        min_opp = 10**9
        for rx, ry in res:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            adv = d_opp - d_self
            # prioritize immediate advantage; then reduce own distance; then reduce opponent distance
            val = adv * 100 - d_self * 3 + d_opp * 0.2 - adj_obst(nx, ny) * 1.5
            if val > a:
                a = val
                min_self = d_self
                min_opp = d_opp
        # prefer moves that keep options: smaller min_self when tied
        t = (a, -min_self, -min_opp)
        cur = (t[0], t[1], (dx, dy))
        if cur[0] > best[0] or (cur[0] == best[0] and cur[1] > best[1]):
            best = cur

    return [best[2][0], best[2][1]]