def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            score = cheb(nx, ny, cx, cy)
            if score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    resources_sorted = sorted(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0], r[1]))
    top_targets = resources_sorted[:6]

    # Try to grab a resource that's better relative to the opponent.
    best_move = (10**9, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        move_score = 10**9
        for rx, ry in top_targets:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Lower ds is good; higher do is good (we're effectively racing).
            val = ds - 0.7 * do
            if (rx, ry) == (nx, ny):
                val -= 5  # strong incentive to pick up immediately
            # Small tie-break to avoid dithering: prefer moving toward that same target y then x.
            val = (val * 1000) + (abs(ry - ny) + abs(rx - nx)) * 3
            if val < move_score:
                move_score = val
        if move_score < best_move[0]:
            best_move = (move_score, dx, dy)
        # Deterministic tie-break
        elif move_score == best_move[0] and (dx, dy) < (best_move[1], best_move[2]):
            best_move = (move_score, dx, dy)

    return [best_move[1], best_move[2]]