def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose target deterministically: maximize distance advantage; break ties by closer to center, then by position.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # positive means we are closer
        dc = abs(rx - cx) + abs(ry - cy)
        key = (-adv, ds, dc, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry), adv)
    (adv_key, (tx, ty), adv) = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # If no advantage, still go for the resource that hurts the opponent most (minimize their advantage after our move).
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        new_adv = no - ns  # we want larger
        # Secondary: reduce our distance; tertiary: prefer moves that increase Manhattan separation from opponent only if it helps.
        dist_self = ns
        dist_opp = cheb(nx, ny, ox, oy)
        if adv > 0:
            val = (-new_adv, dist_self, abs(nx - tx) + abs(ny - ty), -dist_opp, dx, dy)
        else:
            val = (-(new_adv), dist_self, abs(nx - tx) + abs(ny - ty), dist_opp, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]