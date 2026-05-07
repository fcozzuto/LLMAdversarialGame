def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_res = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach earlier; otherwise bias away from opponent-favored ones.
        key = (ds - do * 0.65, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        # Primary: get closer to target
        ds = cheb(nx, ny, rx, ry)
        # Secondary: deny opponent a bit if they are closer to same target after move
        do = cheb(ox, oy, rx, ry)
        # Tertiary: slight preference to move in direction of target (deterministic tie-break)
        dir_pref = (0 if nx == sx else abs(nx - rx) < abs(sx - rx)) + (0 if ny == sy else abs(ny - ry) < abs(sy - ry))
        score = (ds - do * 0.25, ds, -dir_pref, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]