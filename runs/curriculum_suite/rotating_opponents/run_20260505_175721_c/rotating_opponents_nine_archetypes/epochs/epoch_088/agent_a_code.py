def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    center = (w // 2, h // 2)

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0: nx = 0
        if nx >= w: nx = w - 1
        if ny < 0: ny = 0
        if ny >= h: ny = h - 1
        if (nx, ny) in obstacles:
            continue

        self_after = (nx, ny)
        opp_d_to = cheb((ox, oy), center)
        my_cent = cheb(self_after, center)

        # Local lookahead: choose move that maximizes guaranteed/contested reach into any resource.
        score = -10**18
        for tx, ty in resources:
            self_d = cheb(self_after, (tx, ty))
            opp_d = cheb((ox, oy), (tx, ty))
            adv = opp_d - self_d  # positive means we can arrive not slower
            # Prefer resources we can reach quickly; also deny opponent by reducing their advantage.
            s = adv * 120 - self_d * 6 - abs(tx - sx) - abs(ty - sy)
            # Mild tie-break to avoid drifting into opponent edge patrol: prefer staying closer to center.
            s -= (my_cent - opp_d_to) * 2
            if s > score:
                score = s

        # Small deterministic bias to keep progress when scores tie.
        score += (nx - sx) * 0.5 + (ny - sy) * 0.25 - cheb(self_after, (ox, oy)) * 0.05

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]