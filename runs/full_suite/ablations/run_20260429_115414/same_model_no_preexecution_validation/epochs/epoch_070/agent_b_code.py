def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick best resource by deterministic advantage against opponent (distance in Chebyshev metric).
    best_t = None
    best_sc = -10**18
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        adv = do - ds  # positive => we are closer
        # Favor guaranteed grabs (high adv), then being closer; penalize opponent proximity.
        sc = adv * 1000 - ds * 3 - do
        # Mild preference away from being stuck near our own corner if opponent also close
        sc -= (sx == w - 1 and sy == h - 1) * (ds < 3 and do < 3)
        if best_t is None or sc > best_sc or (sc == best_sc and (tx, ty) < best_t):
            best_t, best_sc = (tx, ty), sc

    tx, ty = best_t

    # Move one step greedily toward target, but keep deterministic tie-breaks.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_md = 10**9
    best_sd = 10**9
    # Secondary heuristic: avoid moving to squares too close to opponent if we are already winning.
    pre_adv = cheb(ox, oy, tx, ty) - cheb(sx, sy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        md = cheb(nx, ny, tx, ty)
        sd = cheb(nx, ny, ox, oy)
        # If we are not winning, prioritize getting closer to target; otherwise also reduce opponent closeness a bit.
        score = md * 1000 + (sd * (1 if pre_adv <= 0 else 0) + (1 if pre_adv > 0 else 0) * (-sd))
        if score < best_md * 1000 or (score == best_md * 1000 and (md < best_sd or (md == best_sd and (dx, dy) < best_m))):
            best_m = (dx, dy)
            best_md = md
            best_sd = sd

    return [int(best_m[0]), int(best_m[1])]