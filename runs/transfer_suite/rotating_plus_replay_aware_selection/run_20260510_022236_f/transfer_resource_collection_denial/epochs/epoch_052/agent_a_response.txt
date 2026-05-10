def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    res = []
    for x, y in resources:
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def danger(x, y):
        # discourage walking next to obstacles (denier often forces tight paths)
        d = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obs:
                    d += 1
        return d

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    # Evaluate each possible immediate move by best reachable resource for the next position
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            # engine would keep us; score this as staying
            nx, ny = sx, sy
        if (nx, ny) in obs:
            continue

        best_for_pos = -10**18
        for rx, ry in res:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources we can secure earlier; add mild preference for closer targets
            margin = od - sd
            val = margin * 1000 - sd * 3 - danger(nx, ny) * 5
            # Tie-break: prefer positions that are closer when margins equal
            if val > best_for_pos:
                best_for_pos = val

        # Small preference for making progress toward any resource set (prevents dithering)
        any_dist = 10**9
        for rx, ry in res:
            d = cheb(nx, ny, rx, ry)
            if d < any_dist:
                any_dist = d
        progress_bonus = -any_dist

        total = best_for_pos + progress_bonus
        if total > best_val:
            best_val = total
            best_move = [dx, dy]

    return best_move