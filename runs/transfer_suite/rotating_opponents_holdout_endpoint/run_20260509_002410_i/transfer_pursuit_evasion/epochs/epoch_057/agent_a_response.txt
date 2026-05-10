def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    best_score = None
    best_move = [0, 0]

    # weights tuned for pursuit_evasion with sparse obstacles
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue

        mdx, mdy = nx - ox, ny - oy
        dist2 = mdx * mdx + mdy * mdy

        # Encourage staying aligned with the opponent for pursuer; opposite for evader
        step_dir = (dx == 0 and dy == 0)
        if step_dir:
            align = 0
        else:
            align = (1 if (dx != 0 and (nx - ox) * dx >= 0) else 0) + (1 if (dy != 0 and (ny - oy) * dy >= 0) else 0)
        # Avoid being boxed by moving away from nearby obstacles
        prox = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                    prox += 1

        # Border preference: pursuer likes borders to limit opponent; evader also sometimes likes borders to escape
        on_edge = 1 if (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1) else 0

        # Score: pursuer minimizes dist2; evader maximizes dist2
        if is_evader:
            score = dist2 + 0.7 * prox + 1.2 * on_edge + 0.05 * align
        else:
            score = -dist2 + 0.9 * prox + 0.8 * on_edge + 0.05 * align

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]