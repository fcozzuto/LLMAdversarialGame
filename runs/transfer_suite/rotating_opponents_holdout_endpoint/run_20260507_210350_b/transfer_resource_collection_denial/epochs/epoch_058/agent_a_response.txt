def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    # Target preference: grab resources where we have a decisive arrival advantage;
    # otherwise block by aiming for the resource with the most tie/odd advantage on distance gap.
    best = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        gap = ds - do  # negative means we are faster
        # Strongly prefer faster; otherwise prefer smallest ds and larger distance gap (weirder contest).
        # Deterministic tie-break by coordinates.
        key = (abs(gap), gap, ds, -do, tx, ty)
        if best is None or key < best[0]:
            best = (key, (tx, ty))
    tx, ty = best[1]

    # Move one step toward target with obstacle avoidance using local 3x3 deterministic evaluation.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            dist = cheb(nx, ny, tx, ty)
            # Prefer immediate capture if on resource (dist==0); otherwise greedy by dist.
            # Tie-break: closer to target in L1, then lower dx, then lower dy.
            l1 = abs(nx - tx) + abs(ny - ty)
            moves.append((dist, l1, dx, dy))
    if not moves:
        return [0, 0]
    moves.sort()
    return [int(moves[0][2]), int(moves[0][3])]