def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs = set(tuple(p) for p in (observation.get("obstacles") or []))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def best_resource(px, py):
        if not resources:
            return None
        best = None
        best_score = None
        for rx, ry in resources:
            sd = cheb(px, py, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            center = abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)
            parity = (px + py + rx + ry) & 1
            score = (adv * 1000.0) + (-sd * 10.0) + (-parity * 0.5) + (-center * 0.01)
            if best_score is None or score > best_score or (score == best_score and (rx, ry) < best):
                best_score = score
                best = (rx, ry)
        return best

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    target = best_resource(sx, sy)
    if target is None:
        return [0, 0]
    tx, ty = target

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Prefer moving to reduce our distance to target while maintaining advantage vs opponent.
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = od - sd
        # Tie-break: avoid getting blocked by obstacles, prefer lower coordinates deterministically.
        blocked = 0
        for adx, ady in moves:
            ax2, ay2 = nx + adx, ny + ady
            if not inb(ax2, ay2) or (ax2, ay2) in obs:
                blocked += 1
        score = (adv * 1000.0) + (-sd * 10.0) + (-blocked * 0.1) + (-(nx + ny) * 1e-6)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)
    return [int(best[0]), int(best[1])]