def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick a resource we can reach no worse than opponent, prefer closer with safety against opponent stealing.
    best = None
    best_val = -10**18
    for x, y in resources:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        # Higher is better: beat opponent (do-ds), then prefer small ds, and prefer resources away from opponent.
        val = (do - ds) * 1000 - ds * 3 - (cheb(ox, oy, x, y) < cheb(sx, sy, x, y)) * 0
        # Slight deterministic tie-break favor towards left/up to avoid oscillations.
        val -= x * 0.01 + y * 0.02
        if val > best_val:
            best_val = val
            best = (x, y)
    tx, ty = best

    # Move one step (8-direction via dx/dy in {-1,0,1}); avoid blocked if possible.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                moves.append((dx, dy))
    # If all adjacent are blocked, allow staying or stepping into blocked (engine will keep us if invalid).
    if not moves:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h:
                    moves.append((dx, dy))

    # Score moves by progress to target; also lightly discourage moving into squares where opponent becomes much closer.
    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)  # opponent position fixed this turn
        prog = cheb(sx, sy, tx, ty) - ns
        # tie-break deterministic: prefer dx then dy towards reducing (x,y) offset relative to target.
        hint = 0
        if tx > nx:
            hint -= 0.001
        if ty > ny:
            hint -= 0.001
        val = prog * 100 - ns * 1 + (no - ns) * 0.1 + hint
        scored.append((val, dx, dy))
    scored.sort(key=lambda t: (-t[0], t[1], t[2]))
    dx, dy = scored[0][1], scored[0][2]
    # If already at target, prefer stay (deterministic).
    if sx == tx and sy == ty:
        return [0, 0]
    return [int(dx), int(dy)]