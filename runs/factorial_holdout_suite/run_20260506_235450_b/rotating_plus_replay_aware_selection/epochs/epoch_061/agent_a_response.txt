def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []

    obstacles = set()
    for p in obs_list:
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

    legal = []
    for dx, dy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not resources or not legal:
        return [0, 0]

    def cell_score(rx, ry):
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        if ds <= do:
            # prioritize winning races; tie-break by how much sooner we arrive, then by absolute closeness
            return (1, do - ds, -ds, -(rx + 3 * ry))
        else:
            # if can't win outright, pick denial: where opponent is farther than us (rare), else minimize opponent lead
            return (0, -ds, do - ds, -(rx + 3 * ry))

    best = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        k = cell_score(rx, ry)
        if best_key is None or k > best_key:
            best_key = k
            best = (rx, ry)

    tx, ty = best
    best_move = None
    best_mk = None
    for dx, dy, nx, ny in legal:
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        # extra tie-break: avoid moves that let opponent get closer to target than we do after moving
        mk = (-(0 if ns == no else (no - ns)), -ns, (0 if (ox == nx and oy == ny) else 0), -(dx*dx + dy*dy))
        if best_mk is None or mk > best_mk:
            best_mk = mk
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]