def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Pick a target we can likely collect before opponent; if none, pick best "escape" target.
    best = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        if ds == 0:
            score = 10**9
        else:
            # Prioritize first-access (smaller ds, larger gap), then absolute ds
            gap = do - ds
            # If opponent is closer, prefer resources with larger gap potential (still deterministic)
            score = (gap * 1000) - ds
            if gap < 0:
                score -= 2000
        if best is None or score > best[0]:
            best = (score, rx, ry)
    _, tx, ty = best

    # Greedy step toward target, but avoid moves that increase distance; tie-break with opponent distance.
    cur_ds = cheb(sx, sy, tx, ty)
    best_move = None
    for dx, dy, nx, ny in legal:
        nds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer reducing our distance; if not possible, prefer minimal increase; then farther from opponent.
        delta = nds - cur_ds
        opp_dist = cheb(ox, oy, nx, ny)
        # small obstacle-proximity penalty: don't move adjacent to obstacles if equally good
        adj_obst = 0
        for ddx, ddy in dirs:
            ax, ay = nx + ddx, ny + ddy
            if (ax, ay) in obst:
                adj_obst += 1
        key = (delta, adj_obst, -opp_dist, nds, dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)
    return [best_move[1], best_move[2]]