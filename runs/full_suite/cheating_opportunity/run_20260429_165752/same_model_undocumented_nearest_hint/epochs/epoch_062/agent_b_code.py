def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [W - 1, H - 1]) or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    if not resources:
        best = (None, -10**9, 10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            ddo = cheb(nx, ny, ox, oy)
            # Prefer moving away; tie-break: stay closer to board center.
            center = abs(nx - (W - 1) / 2) + abs(ny - (H - 1) / 2)
            cand = (dx, dy, ddo, -center)
            if (cand[2], cand[3]) > (best[1], best[2]):
                best = (cand[:2], cand[2], cand[3])
        return best[0] if best[0] is not None else [0, 0]

    # Pick a target that I can reach at least as fast as (or faster than) opponent; otherwise pick the one where
    # I can maximize opponent delay.
    best_t = None
    best_key = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Primary: minimize ds; Secondary: maximize (do - ds); Tertiary: deterministic ordering by coords.
        key = (-(do - ds), ds, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    best_move = (0, 0)
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        # Prefer moving closer to target; also prefer targets where opponent is farther from the path (via larger do2).
        # Tie-break: maximize my distance from opponent after move; then deterministic.
        key = (ds2, -(do2), -(cheb(nx, ny, ox, oy)), dx, dy)
        if best is None or key < best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]