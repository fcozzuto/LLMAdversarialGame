def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = (observation.get("self_role", "") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "fugitive"))
    is_pursuer = any(k in role for k in ("pursuer", "hunter", "seeker"))
    if not is_evader and not is_pursuer:
        is_pursuer = True

    obs = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    deltas.sort(key=lambda d: (d[0], d[1]))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def min_ob_dist(x, y):
        md = 10**9
        for bx, by in obs:
            d = abs(x - bx) + abs(y - by)
            if d < md:
                md = d
        return md if md != 10**9 else 5

    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        dist = abs(nx - ox) + abs(ny - oy)
        md = min_ob_dist(nx, ny)

        # pursuer: minimize dist, strongly penalize moving close to obstacles
        # evader: maximize dist, softly penalize moving close to obstacles
        if is_pursuer:
            val = (-dist) + (md * 0.25) + (0.03 * (abs(nx - (w - 1)) + abs(ny - (h - 1)) - abs(sx - (w - 1)) - abs(sy - (h - 1))))
        else:
            val = (dist * 1.0) + (md * 0.08)

        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]