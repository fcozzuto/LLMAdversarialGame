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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Phase 1: immediate grab or deny
    best = None
    best_pr = -10**9
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        if ds <= 1 and do > 1:
            pr = 10**6 + (2 - ds) * 1000 + (tx - 0) - (ty - 0)
            if pr > best_pr:
                best_pr = pr
                best = (tx, ty)
    if best is None:
        # Phase 2: pick target that we can reach sooner (and that opponent is not closer to)
        for tx, ty in resources:
            ds = cheb(sx, sy, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Prefer resources where we are relatively closer; slight preference to center
            pr = (do - ds) * 1000 - ds * 5 + (3.5 - abs(tx - 3.5)) + (3.5 - abs(ty - 3.5))
            if pr > best_pr:
                best_pr = pr
                best = (tx, ty)

    tx, ty = best
    # Phase 3: choose step that most improves our distance to target while also not allowing opponent a quick capture
    cur_ds = cheb(sx, sy, tx, ty)
    cur_do = cheb(ox, oy, tx, ty)
    chosen = (0, 0)
    best_step = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = cheb(nx, ny, tx, ty)
        # opponent potential next turn distance to target
        odo = 10**9
        for pdx, pdy in moves:
            px, py = ox + pdx, oy + pdy
            if valid(px, py):
                odo = min(odo, cheb(px, py, tx, ty))
        # Score: reduce our distance primarily; penalize if opponent can get close after our move
        step_sc = (cur_ds - nds) * 2000 - nds * 20 + (cur_do - odo) * 50
        if (nx, ny) == (tx, ty):
            step_sc += 10**8
        if step_sc > best_step or (step_sc == best_step and (dx, dy) < chosen):
            best_step = step_sc
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]