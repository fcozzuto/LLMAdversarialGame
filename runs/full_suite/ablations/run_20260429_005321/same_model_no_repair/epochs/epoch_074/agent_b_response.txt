def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def occ(x, y):
        return (x, y) in obst

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    # Target selection: prefer resources where we are not behind, otherwise reduce the gap.
    best_score = 10**18
    best_t = None
    for rx, ry in resources:
        if occ(rx, ry):
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Negative means we are earlier; prioritize earlier, but still compete when behind.
        rel = ds - do
        # Mild preference for closer resources overall.
        s = rel * 10 + ds
        # If opponent is effectively on top, deprioritize unless we can improve soon.
        if do <= 1 and ds > do:
            s += 50
        if s < best_score:
            best_score = s
            best_t = (rx, ry)

    if best_t is None:
        return [0, 0]
    rx, ry = best_t

    # Move evaluation: pick move that best reduces our distance; also avoid moves that let opponent get relatively closer.
    cur_ds = cheb(sx, sy, rx, ry)
    cur_do = cheb(ox, oy, rx, ry)

    def near_obst_pen(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obst:
                    p += 1
        return p

    best_m = (0, 0)
    best_v = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if occ(nx, ny):
            continue
        nds = cheb(nx, ny, rx, ry)
        # Assume opponent moves optimally to that same resource; we approximate by using current opponent dist after our move.
        # Penalize giving opponent a smaller relative advantage.
        rel_before = cur_ds - cur_do
        rel_after = nds - cur_do
        v = (rel_after * 10) + nds
        v += near_obst_pen(nx, ny) * 2
        # Slightly prefer moving closer to opponent when we are behind (interception).
        if rel_before > 0 and rel_after < rel_before:
            v -= 2
        # If opponent is very close to the target, prioritize our fastest approach.
        if cur_do <= 1:
            v -= 3 if nds < cur_ds else 0
        if v < best_v:
            best_v = v
            best_m = (dx, dy)

    return [best_m[0], best_m[1]]