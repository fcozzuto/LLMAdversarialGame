def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def obstacle_pen(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    pen += 2
        return pen

    def opp_block_pen(x, y):
        # discourage stepping into opponent's immediate reach
        return 4 if cheb(x, y, ox, oy) <= 1 else 0

    # Strategy shift: target a resource that is "good for us and awkward for them"
    # Score target = -distance_from_us + slight bias toward their distance
    if resources:
        best_t = None
        best_v = None
        for tx, ty in resources:
            vu = -cheb(sx, sy, tx, ty)
            vo = cheb(ox, oy, tx, ty)
            v = (vu * 10) + (vo * 1)  # maximize
            if best_v is None or v > best_v or (v == best_v and (tx, ty) < best_t):
                best_v = v
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        # no resources: move away from opponent while avoiding obstacles
        tx, ty = (ox, oy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Primary: move closer to target
        dist_t = cheb(nx, ny, tx, ty)
        dist_u = cheb(sx, sy, tx, ty)
        approach = dist_u - dist_t  # positive if closer

        # Secondary: keep distance from opponent to avoid grabs
        dist_o = cheb(nx, ny, ox, oy)

        # Tertiary: avoid obstacle-adjacent squares
        s = (approach * 30) + (dist_o * 2) - obstacle_pen(nx, ny) - opp_block_pen(nx, ny)

        if best_score is None or s > best_score or (s == best_score and (dx, dy) < best_move):
            best_score = s
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]