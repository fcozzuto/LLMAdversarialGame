def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a resource where we have the most distance advantage vs opponent.
    best = None
    best_adv = -10**18
    best_selfd = 10**9
    for r in resources:
        selfd = cheb((sx, sy), r)
        oppd = cheb((ox, oy), r)
        adv = oppd - selfd
        if adv > best_adv or (adv == best_adv and selfd < best_selfd):
            best_adv = adv
            best_selfd = selfd
            best = r

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Try improving move among 8-neighborhood by reducing distance to chosen target,
    # with a small bias to keep moving toward it and away from opponent.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_val = -10**18
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb((nx, ny), (tx, ty))
        od = cheb((ox, oy), (tx, ty))
        # lower nd is better; higher (od - nd) is better; tie-break toward non-wait and toward axis/diag progress
        val = (od - nd) * 100 - nd
        if (mdx, mdy) != (0, 0):
            val += 1
        if mdx == dx or mdy == dy:
            val += 1
        if val > best_val:
            best_val = val
            best_m = (mdx, mdy)

    return [int(best_m[0]), int(best_m[1])]