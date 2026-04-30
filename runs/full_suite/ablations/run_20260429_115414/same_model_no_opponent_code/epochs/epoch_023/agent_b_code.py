def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = observation.get("obstacles") or []
    obs = {(int(p[0]), int(p[1])) for p in obstacles}
    resources = observation.get("resources") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick a target resource with best "competitive edge": self is closer than opponent.
    best = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Edge: positive when self is strictly closer. Tie-break deterministically by position.
        edge = (do - ds)
        # Prefer resources that are not blocked from approach too badly (local).
        around = 0
        for dx, dy in moves:
            nx, ny = rx + dx, ry + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                around += 1
        key = (edge, around, -ds, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    # If no resources, drift to a corner-facing "pressure" point: opposite corner from opponent.
    if best is None:
        tx, ty = (w - 1 - ox, h - 1 - oy)
    else:
        tx, ty = best

    # Move toward target with deterministic obstacle-aware tie-break.
    # Prefer steps that reduce distance to target; secondarily prefer increasing distance to opponent.
    curd = cheb(sx, sy, tx, ty)
    best_move = (0, 0)
    best_tuple = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nd = cheb(nx, ny, tx, ty)
        # If the target is contested (opponent closer), sometimes stepping "sideways" helps.
        # So we also value maintaining/creating a distance gap vs opponent.
        no = cheb(nx, ny, ox, oy)
        # Deterministic tie-breaking uses position order.
        t = (-(nd - curd), -nd, (no - cheb(ox, oy, tx, ty)), nx, ny)
        if best_tuple is None or t > best_tuple:
            best_tuple = t
            best_move = (dx, dy)

    # Safety: if no legal moves found (should be rare), attempt staying still.
    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [int(dx), int(dy)]