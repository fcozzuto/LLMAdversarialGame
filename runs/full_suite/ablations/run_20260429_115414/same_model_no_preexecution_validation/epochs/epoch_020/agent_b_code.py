def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs_set = set()
    for p in obstacles:
        if p is None or len(p) < 2: 
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs_set.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in obs_set
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def obs_pen(x, y):
        if not obs_set: 
            return 0.0
        m = 99
        for px, py in obs_set:
            d = cheb(x, y, px, py)
            if d < m: m = d
        if m <= 1: return 2.7
        if m == 2: return 1.2
        return 0.0

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move, best_val = (0, 0), -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Resource-contest heuristic: prefer resources where we can arrive no later than opponent,
        # and among those, prefer largest advantage after making this move.
        if resources:
            cur_best = -10**18
            for rx, ry in resources:
                s_d = cheb(nx, ny, rx, ry)
                o_d = cheb(ox, oy, rx, ry)
                # Try to "steal" when we are closer (o_d - s_d positive), otherwise chase still if it blocks.
                steal = (o_d - s_d)
                # Encourage reaching quickly and not wandering:
                time = -0.6 * s_d
                # Encourage keeping a resource in reach from here, even if not best:
                cur = steal + time - 0.25 * obs_pen(nx, ny)
                if cur > cur_best:
                    cur_best = cur
            val = cur_best - 0.15 * obs_pen(nx, ny) + 0.02 * cheb(ox, oy, nx, ny) * 0.0
        else:
            # No resources: move toward center while keeping distance from opponent and avoiding obstacles.
            center = -0.12 * (cheb(nx, ny, int(round(cx)), int(round(cy))))
            away = 0.08 * cheb(nx, ny, ox, oy)
            val = center + away - 0.25 * obs_pen(nx, ny)

        # Deterministic tie-break: fixed dir order already, so only strictly greater.
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [int(dx), int(dy)]