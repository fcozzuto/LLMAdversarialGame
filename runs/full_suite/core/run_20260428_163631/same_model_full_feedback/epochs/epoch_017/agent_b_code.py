def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = resources[0]
        best = (-10**18, None)
        for r in resources:
            rx, ry = r
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer immediate pickup, then resources we can reach earlier.
            # Mild anti-rival term: avoid resources opponent is much closer to.
            immediate = 1 if (rx, ry) in resources and ds == 0 else 0
            value = immediate * 10**12
            value += (do - ds) * 10**6
            value += (-ds) * 10
            # Small bias toward the global center to break ties deterministically.
            value += -cheb(rx, ry, w // 2, h // 2)
            if value > best[0]:
                best = (value, r)
        tx, ty = best[1]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        # Choose move that gets us closer to target, while not allowing opponent to immediately steal.
        d_to_target = cheb(nx, ny, tx, ty)
        d_opp_target = cheb(ox, oy, tx, ty)
        # If we are on a resource now, prioritize hard.
        on_res = 1 if (nx, ny) in resources else 0
        score = on_res * 10**12
        score += (-d_to_target) * 10**5
        # If opponent can reach target in <= we can, reduce attractiveness unless we are equal/leading.
        ds_next = cheb(nx, ny, tx, ty)
        do_here = d_opp_target
        score += (do_here - ds_next) * 10
        # Extra tie-break: prefer moves that don't increase opponent's distance to their nearest resource too little.
        # Deterministic center bias.
        score += -cheb(nx, ny, w // 2, h // 2)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]