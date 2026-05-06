def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    opprow_pen = 3
    def pick_metric(px, py, r):
        x, y = r
        d = abs(x - px) + abs(y - py)
        if y == oy:
            d += opprow_pen
        return d

    # choose a "primary" target deterministically with slight anti-sweep-row bias
    target = min(resources, key=lambda r: (pick_metric(sx, sy, r), r[0], r[1]))
    tx, ty = target

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18
    cur_dist = abs(tx - sx) + abs(ty - sy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            # if engine would reject, avoid but still allow staying behavior by treating as no progress
            val = -10**12
        else:
            new_dist = abs(tx - nx) + abs(ty - ny)
            progress = cur_dist - new_dist

            # collision/competition control: avoid being too close to opponent unless it also increases resource progress a lot
            oppd = abs(nx - ox) + abs(ny - oy)
            close_pen = 0
            if oppd <= 1:
                close_pen = 40
            elif oppd <= 2:
                close_pen = 18

            # secondary: keep option to grab a resource near our current row band if target is blocked by race
            # (deterministic but cheap)
            alt = min(resources, key=lambda r: (abs(r[1] - ny) + abs(r[0] - nx), r[0], r[1]))
            alt_bonus = max(0, 3 - (abs(alt[0] - nx) + abs(alt[1] - ny)))

            # bias to move away from opponent's sweeping line when possible (same y as opponent)
            y_bias = 0
            if ny == oy:
                y_bias = -6

            val = progress * 12 + alt_bonus * 2 + y_bias - close_pen + (1 if (nx, ny) == target else 0) * 50

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move