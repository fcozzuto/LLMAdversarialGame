def choose_move(observation):
    w = observation.get("grid_width", 8); h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)] + [(0, 0)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked
    def man(a, b):
        x1, y1 = a; x2, y2 = b
        d = x1 - x2; d = -d if d < 0 else d
        e = y1 - y2; e = -e if e < 0 else e
        return d + e

    if not resources:
        tx, ty = w // 2, h // 2
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                sc = man((nx, ny), (tx, ty))
                if sc < best[0]:
                    best = (sc, dx, dy)
        return [best[1], best[2]]

    best_res = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2): 
            continue
        x, y = r[0], r[1]
        if not (isinstance(x, int) and isinstance(y, int) and inb(x, y)):
            continue
        ds = man((sx, sy), (x, y))
        do = man((ox, oy), (x, y))
        gap = ds - do  # smaller => you are closer or less behind
        # tie-break deterministically: prefer smaller ds then lexicographic (x,y)
        key = (gap, ds, x, y)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (x, y)

    tx, ty = best_res
    # Step toward target with obstacle-respecting fallback: choose neighbor minimizing (dist to target, self-target advantage)
    best = (10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ns = man((nx, ny), (tx, ty))
        no = man((ox, oy), (tx, ty))
        key = (ns - no, ns, abs(nx - tx) + abs(ny - ty), nx, ny)
        if key < (best[0],):  # dummy, keep structure
            pass
        if key[0] < best[0] or (key[0] == best[0] and (key[1], key[2], key[3], key[4]) < best[1:]):
            best = (key[0], dx, dy)
    return [best[1], best[2]]