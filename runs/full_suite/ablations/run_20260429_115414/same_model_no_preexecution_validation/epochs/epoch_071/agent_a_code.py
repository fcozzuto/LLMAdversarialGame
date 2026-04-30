def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cell_score(tx, ty):
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Favor targets I can reach sooner; add slight bias for being farther from my own position already.
        return (do - ds) * 1000 - ds

    # Pick best target with deterministic tie-breaks
    best = None
    best_sc = -10**18
    for tx, ty in resources:
        sc = cell_score(tx, ty)
        if sc > best_sc or (sc == best_sc and (tx, ty) < (best[0], best[1]) if best else True):
            best_sc = sc
            best = (tx, ty)
    tx, ty = best

    # If a resource is reachable this turn, take it
    if cheb(sx, sy, tx, ty) <= 1:
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny) and (nx, ny) == (tx, ty):
                return [dx, dy]

    # Move one step toward target, breaking ties by improving relative advantage vs opponent.
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_ms = -10**18
    cur_ds = cheb(sx, sy, tx, ty)
    cur_do = cheb(ox, oy, tx, ty)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = cheb(nx, ny, tx, ty)
        # If we reduce my distance, strongly preferred.
        delta_ds = cur_ds - nds
        # Also prefer moves that (heuristically) reduce opponent's chance: increase separation to opponent overall.
        sep_now = cheb(sx, sy, ox, oy)
        sep_next = cheb(nx, ny, ox, oy)
        rel = cur_do - nds  # relative advantage if opponent stays
        ms = delta_ds * 5000 + rel * 200 + (sep_next - sep_now) *