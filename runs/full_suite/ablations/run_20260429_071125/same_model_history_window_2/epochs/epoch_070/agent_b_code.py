def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best_target = None
    best_key = None
    for x, y in resources:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        # Prefer targets where we are closer; if not, prefer those far from opponent.
        key = (-(ds - do), -ds, do, x, y)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (x, y)

    if best_target is None:
        # Fallback: drift away from opponent toward center
        cx, cy = w // 2, h // 2
        tx, ty = cx, cy
    else:
        tx, ty = best_target

    # Choose move that heads to target while minimizing opponent's advantage gain.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Opponent after our move (one step): approximate by best possible reduction.
        min_do_next = 10**9
        for odx, ody in moves:
            onx, ony = ox + odx, oy + ody
            if ok(onx, ony):
                d = cheb(onx, ony, tx, ty)
                if d < min_do_next:
                    min_do_next = d
        # Score: smaller ds better; larger (min_do_next - ds) better.
        score = (-(ds), (min_do_next - ds), -do, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]