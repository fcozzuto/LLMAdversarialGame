def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "pursuer")).lower()
    evading = ("evader" in role) or ("runner" in role)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        return max(abs(ax - bx), abs(ay - by))

    best = None
    best_score = None

    # Small bias so ties break deterministically towards "forward" (dx,dy later in list give later priority)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        d_opp = cheb(nx, ny, ox, oy)
        d_corner = max(cheb(nx, ny, cx, cy) for cx, cy in corners)

        # Pursuer: minimize distance to opponent; Evader: maximize.
        # Add obstacle proximity penalty: avoid stepping adjacent to obstacles.
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in blocked:
                    adj_obs += 1

        if evading:
            score = (d_opp * 1000) + (d_corner * 3) - (adj_obs * 25)
            better = (best_score is None) or (score > best_score)
        else:
            score = (-d_opp * 1000) + (d_corner * 0) - (adj_obs * 25)
            better = (best_score is None) or (score > best_score)

        if better:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]