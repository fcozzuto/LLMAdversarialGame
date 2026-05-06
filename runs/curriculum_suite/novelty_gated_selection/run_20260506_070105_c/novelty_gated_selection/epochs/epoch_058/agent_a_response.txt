def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(tuple(o) for o in (observation.get("obstacles", []) or []))
    resources = []
    for r in (observation.get("resources", []) or []):
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) not in obstacles:
            resources.append((rx, ry))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def clamp(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        return [dx, dy]

    # Pick resource maximizing advantage over opponent; if unsure, prefer closer.
    best = None
    best_sc = -10**9
    for rx, ry in resources:
        my_d = dist((sx, sy), (rx, ry))
        opp_d = dist((ox, oy), (rx, ry))
        # advantage: larger means opponent farther than me
        adv = opp_d - my_d
        align = abs((rx - sx) - (ry - sy))  # smaller is better (more diagonal-ish)
        sc = (adv * 3) - (my_d * 1) - (align * 0.25)
        if sc > best_sc:
            best_sc = sc
            best = (rx, ry)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Choose legal step that minimizes distance to target; avoid obstacles if possible.
    best_m = [0, 0]
    best_md = 10**9
    best_ood = 10**9  # tie-break: don't move closer to opponent unnecessarily
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp(nx, ny):
            continue
        if (nx, ny) in obstacles:
            # Still consider if no alternative exists
            md = dist((nx, ny), (tx, ty)) + 1000
            ood = dist((nx, ny), (ox, oy))
        else:
            md = dist((nx, ny), (tx, ty))
            ood = dist((nx, ny), (ox, oy))
        if md < best_md or (md == best_md and ood > best_ood):
            best_md = md
            best_ood = ood
            best_m = [dx, dy]

    return [int(best_m[0]), int(best_m[1])]