def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # Pick target: prefer resources we are closer to than opponent; otherwise pick best tradeoff
    best_t = None
    best_k = None
    for tx, ty in resources:
        ds = dist2(sx, sy, tx, ty)
        do = dist2(ox, oy, tx, ty)
        closer_adv = (do - ds)  # positive if we are closer
        # Key: prioritize being clearly closer, then prefer far-from-opponent pickup positions
        k = (closer_adv * 2) + (do - ds) + (-ds)
        if best_k is None or k > best_k:
            best_k = k
            best_t = (tx, ty)

    if best_t is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best_t

    # Greedy 1-step: move toward target while keeping distance from opponent and avoiding corners
    best_m = (0, 0)
    best_s = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to_t = dist2(nx, ny, tx, ty)
        d_to_o = dist2(nx, ny, ox, oy)
        # Encourage progress: lower d_to_t, higher d_to_o; also slightly prefer staying away from obstacles by bounds
        wall_pen = 0
        if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
            wall_pen = 1
        s = (-d_to_t * 2) + (d_to_o) - wall_pen
        # If current move reaches/adjacent to a resource, boost strongly
        if (nx, ny) in set(resources):
            s += 10**6
        best_target_next = False
        for rx, ry in resources:
            if abs(nx - rx) <= 1 and abs(ny - ry) <= 1:
                best_target_next = True
                break
        if best_target_next:
            s += 5000
        if s > best_s:
            best_s = s
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]