def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Prefer resources that are both reasonably close to us and "more central" (opponent tends to patrol edges).
    def resource_value(t):
        sd = man((sx, sy), t)
        od = man((ox, oy), t)
        center = (-(abs(t[0] - cx) + abs(t[1] - cy)))
        # Larger is better
        return (od - sd, -sd, center, -abs(t[0] - sx) - abs(t[1] - sy), -t[0] - t[1])

    target = None
    best = None
    for t in resources:
        v = resource_value(t)
        if best is None or v > best:
            best, target = v, t

    tx, ty = target
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose move that improves our position relative to the target and overall resources.
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            # Likely rejected by engine; heavily penalize
            score = (-10**9, 0)
        else:
            # primary: get closer to target
            sd1 = abs(nx - tx) + abs(ny - ty)
            # secondary: deny opponent by increasing distance advantage on nearest resource from the new position
            # (use a small deterministic scan over top few resources to keep it cheap)
            cand = 0
            # pick up to 5 deterministic resources: those closest to our current pos
            ranked = sorted(resources, key=lambda r: (man((sx, sy), r), r[0], r[1]))[:5]
            best_adv = None
            for r in ranked:
                self_d = abs(nx - r[0]) + abs(ny - r[1])
                opp_d = abs(ox - r[0]) + abs(oy - r[1])
                adv = opp_d - self_d
                if best_adv is None or adv > best_adv:
                    best_adv = adv
                cand += (self_d == 0)
            center = -(abs(nx - cx) + abs(ny - cy))
            score = (best_adv, -sd1, center, cand, -abs(ox - nx) - abs(oy - ny))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move