def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            resources.append((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    def clamp_step(dx, dy):
        if dx < 0: dx = -1
        elif dx > 0: dx = 1
        else: dx = 0
        if dy < 0: dy = -1
        elif dy > 0: dy = 1
        else: dy = 0
        return dx, dy

    # Pick a target we can reach sooner than the opponent; deterministic tie-breaks.
    tx, ty = ox, oy
    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we're closer (do - ds), then smaller ds, then deterministic coords.
            key = (do - ds, -ds, -(rx + 7 * ry), rx, ry)
            if best is None or key > best[0]:
                best = (key, rx, ry)
        _, tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d_tar = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)

        # Move toward target, keep distance from opponent, and slightly discourage staying.
        step_pen = 0 if (dx == 0 and dy == 0) else 0.05
        # Also discourage positions that let opponent get strictly closer next to same target.
        opp_after = cheb(ox, oy, tx, ty)
        self_after = d_tar
        tempo = (opp_after - self_after)

        val = (10 * tempo) - (2.0 * d_tar) + (0.7 * d_opp) - step_pen

        # Deterministic tie-break by (dx,dy) preference order: nearer diagonal/forward then lower dx/dy.
        tieb = (abs(dx) + abs(dy), -dx, -dy, dx, dy)
        if best_val is None or (val > best_val) or (val == best_val and tieb > best_tieb):
            best_val = val
            best_tieb = tieb
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]