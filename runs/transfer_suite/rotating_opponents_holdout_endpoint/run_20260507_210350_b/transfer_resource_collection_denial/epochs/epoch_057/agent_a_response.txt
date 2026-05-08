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

    best_targets = []
    best_key = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer resources where we can arrive earlier; also prefer those with opponent disadvantage.
        key = (do - ds, -(ds + 0.15 * do), tx, ty)  # deterministic tie-break
        if best_key is None or key > best_key:
            best_key = key
            best_targets = [(tx, ty)]
        elif key == best_key:
            best_targets.append((tx, ty))
    tx, ty = sorted(best_targets)[0]

    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            deltas.append((dx, dy))

    cur_resource = (sx, sy) in resources
    best_move = (0, 0)
    best_move_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        # Aim to reach the chosen target; if we're already on a resource, hover with slight bias to nearby.
        dist_bias = ns - 0.65 * no
        on_next = (nx, ny) in resources
        val = (-(dist_bias), on_next, -cheb(nx, ny, tx, ty), -dx, -dy)
        if best_move_val is None or val > best_move_val:
            best_move_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]