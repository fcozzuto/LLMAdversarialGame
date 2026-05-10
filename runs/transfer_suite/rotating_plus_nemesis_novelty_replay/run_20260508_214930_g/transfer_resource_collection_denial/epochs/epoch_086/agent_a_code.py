def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    seen = set()
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles and (x, y) not in seen:
                seen.add((x, y))
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    center = ((w - 1) / 2.0, (h - 1) / 2.0)
    best = None  # (score tuple, dx, dy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Prefer moves that likely secure a resource before opponent, then move closer to center.
        # Use max over resources: advantage if we reach that resource sooner (Chebyshev).
        best_adv = -10**9
        best_selfd = 10**9
        best_cdist = 10**9
        for rx, ry in resources:
            self_d = cheb((nx, ny), (rx, ry))
            opp_d = cheb((ox, oy), (rx, ry))
            adv = opp_d - self_d
            if adv > best_adv or (adv == best_adv and (self_d < best_selfd or (self_d == best_selfd and cheb((nx, ny), center) < best_cdist))):
                best_adv = adv
                best_selfd = self_d
                best_cdist = cheb((nx, ny), center)

        # Small deterministic tie-break favoring diagonal (more flexible) then towards increasing x then y.
        tie = (0 if dx != 0 and dy != 0 else 1, -dx, -dy)
        score = (best_adv, -best_selfd, -best_cdist, tuple(tie))
        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]