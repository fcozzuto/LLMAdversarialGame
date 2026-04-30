def choose_move(observation):
    W = observation.get('grid_width', 8)
    H = observation.get('grid_height', 8)
    x, y = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))

    def inb(a, b): return 0 <= a < W and 0 <= b < H
    def dist_cheb(ax, ay, bx, by): 
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx if dx > dy else dy
    def blocked(nx, ny): return (nx, ny) in obstacles

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        # No resources: move to center while keeping away from opponent.
        cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
        best = None; bestv = None
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or blocked(nx, ny): 
                continue
            v = dist_cheb(nx, ny, int(cx), int(cy)) - 0.7 * dist_cheb(nx, ny, ox, oy)
            if bestv is None or v < bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    # Pick resource where we arrive earlier than opponent; deterministic tie-breaks.
    best_t = None; best_sc = None; best_ds = None
    for rx, ry in resources:
        if (rx, ry) in obstacles: 
            continue
        ds = dist_cheb(x, y, rx, ry)
        do = dist_cheb(ox, oy, rx, ry)
        sc = ds - 0.85 * do  # smaller is better (we want advantage)
        if best_sc is None or sc < best_sc or (sc == best_sc and (best_ds is None or ds < best_ds)) or (sc == best_sc and ds == best_ds and (rx + ry) < (best_t[0] + best_t[1])):
            best_sc = sc; best_ds = ds; best_t = (rx, ry)

    tx, ty = best_t
    cur_d = dist_cheb(x, y, tx, ty)

    # Choose move that decreases distance most; avoid obstacles; also mildly prefer moving away from opponent when tied.
    best = (0, 0); bestv = (10**9, 10**9, 10**9)
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        nd = dist_cheb(nx, ny, tx, ty)
        if nd > cur_d + 0:  # don't worsen unless forced later by all blocked
            pass
        oppd = dist_cheb(nx, ny, ox, oy)
        # Primary: minimize nd; Secondary: maximize oppd; Tertiary: deterministic preference by dx,dy
        v = (nd, -oppd, (dx + 2) * 10 + (dy + 2))
        if v < bestv:
            bestv = v; best = (dx, dy)

    # If every move was blocked/out of bounds, stay (engine may keep position anyway).
    return [int(best[0]), int(best[1])]