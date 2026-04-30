def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Strategic change: prioritize resources that are closer to us AND farther from opponent,
    # so we contest less and grab more unique territory.
    bestt = None
    bestscore = None
    for x, y in res:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        # Lower is better: our distance, plus penalty if opponent is also close.
        score = ds * 2 - min(do, 7)  # bounded influence
        if bestscore is None or score < bestscore or (score == bestscore and (x, y) < bestt):
            bestscore = score
            bestt = (x, y)

    tx, ty = bestt

    # Move greedily with deterministic obstacle-aware tie-breaking.
    best = (0, 0)
    bestd = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, tx, ty)
            # Tie-break: prefer moves that increase opponent distance from their target roughly.
            opp_focus = cheb(ox, oy, tx, ty)
            oppd = cheb(ox, oy, tx, ty)  # unchanged (opponent moves later); keep stable deterministic
            # Also prefer staying inside board and not moving toward obstacles' immediate adjacency.
            adj_obs = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    xx, yy = nx + ax, ny + ay
                    if (xx, yy) in obstacles:
                        adj_obs += 1
            cand = (d, adj_obs, abs(dx) + abs(dy), oppd)
            if bestd is None or cand < bestd:
                bestd = cand
                best = (dx, dy)

    if bestd is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]