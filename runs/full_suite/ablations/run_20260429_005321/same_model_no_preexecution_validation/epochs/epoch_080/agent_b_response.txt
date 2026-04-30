def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    def obs_adj(x, y):
        c = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in obstacles:
                c += 1
        return c

    def score_pos(mx, my):
        if not resources:
            cx, cy = w // 2, h // 2
            return -cheb(mx, my, cx, cy) - 0.1 * obs_adj(mx, my)
        best = -10**18
        for rx, ry in resources:
            d_me = cheb(mx, my, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            adv = d_op - d_me  # closer than opponent => positive
            v = 3.0 * adv - 0.7 * d_me - 0.08 * obs_adj(mx, my)
            if mx == rx and my == ry:
                v += 1000.0
            if v > best:
                best = v
        # small penalty for moving away from opponent "lane" to avoid dead ends
        best -= 0.03 * cheb(mx, my, ox, oy)
        return best

    best_move = (0, 0)
    best_score = -10**18
    # Deterministic tie-break order: dirs in the listed order
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            sc = -10**18
        else:
            sc = score_pos(nx, ny)
        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]