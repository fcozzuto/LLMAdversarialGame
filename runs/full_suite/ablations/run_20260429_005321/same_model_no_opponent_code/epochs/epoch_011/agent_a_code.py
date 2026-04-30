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
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # Fallback: move toward center-ish of opponent/opposite diagonal deterministically
        tx, ty = (w // 2, h // 2)
        best = [0, 0]
        bestv = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            v = cheb(nx, ny, tx, ty)
            if bestv is None or v < bestv or (v == bestv and (dx, dy) < tuple(best)):
                bestv = v
                best = [dx, dy]
        return best

    # Pick best resource by immediate advantage against opponent (no randomness)
    best_r = resources[0]
    best_adv = None
    best_ds = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds
        if best_adv is None or adv > best_adv or (adv == best_adv and (best_ds is None or ds < best_ds)) or (
            adv == best_adv and ds == best_ds and (rx, ry) < best_r
        ):
            best_adv = adv
            best_ds = ds
            best_r = (rx, ry)

    rx, ry = best_r

    # Choose move that improves advantage while heading to target; also avoid getting blocked.
    cur_ds = cheb(sx, sy, rx, ry)
    cur_do = cheb(ox, oy, rx, ry)
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        nds = cheb(nx, ny, rx, ry)
        ndo = cur_do  # opponent position unchanged during our move
        adv = ndo - nds
        # Tie-break: prefer smaller nds, then deterministic by (dx,dy)
        score = (adv * 1000) - nds
        if best_score is None or score > best_score or (score == best_score and (nds < cheb(sx + best_move[0], sy + best_move[1], rx, ry))) or (
            score == best_score
            and nds == cheb(sx + best_move[0], sy + best_move[1], rx, ry)
            and (dx, dy) < tuple(best_move)
        ):
            best_score = score
            best_move = [dx, dy]

    # If target is already on our square, stay still (deterministic)
    if (sx, sy) == (rx, ry):
        return [0, 0]
    return best_move