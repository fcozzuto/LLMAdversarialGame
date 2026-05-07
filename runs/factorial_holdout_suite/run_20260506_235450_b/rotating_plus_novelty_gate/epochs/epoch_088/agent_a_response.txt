def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    rs = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and valid(x, y):
                rs.append((x, y))
    if not rs:
        return [0, 0]

    # Select target with best "win" advantage: opponent farther than us, prioritized.
    best_t = None
    best_sc = -10**18
    best_sd = 10**9
    for (tx, ty) in rs:
        sd = manh(sx, sy, tx, ty)
        od = manh(ox, oy, tx, ty)
        sc = od - sd
        if sc > best_sc or (sc == best_sc and sd < best_sd):
            best_sc, best_sd, best_t = sc, sd, (tx, ty)
    tx, ty = best_t

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_v = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Prefer reducing distance; if equal, prefer moving "toward" target in Chebyshev sense.
        nd = manh(nx, ny, tx, ty)
        # Secondary: also keep an eye on opponent closeness to that same target.
        nod = manh(ox, oy, tx, ty)
        v = (-(nd * 10 + (0 if nod >= best_sd else 5)) ) + (best_sc * 0)
        if v > best_v:
            best_v = v
            best_m = (dx, dy)

    if best_m == (0, 0) and not valid(sx, sy):
        return [0, 0]
    return [best_m[0], best_m[1]]