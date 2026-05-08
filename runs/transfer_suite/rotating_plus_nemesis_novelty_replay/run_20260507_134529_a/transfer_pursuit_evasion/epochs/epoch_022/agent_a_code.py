def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x, y):
        dx = x - ox
        if dx < 0: dx = -dx
        dy = y - oy
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def mob(x, y):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if inb(nx, ny):
                    c += 1
        return c

    def near_obst(x, y):
        # Count adjacent blocked cells (walls) to avoid getting trapped.
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if not (0 <= nx < w and 0 <= ny < h):
                    c += 1
                elif (nx, ny) in obstacles:
                    c += 1
        return c

    self_role = (observation.get("self_role") or "")
    pursuer = ("pursuer" in self_role.lower()) or (self_role.lower() == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = None
    best_mv = (0, 0)

    # Wall-runner counter: prioritize moves that (1) reduce distance, (2) keep mobility high,
    # (3) avoid positions with many adjacent blocked cells, and (4) don't go toward dead ends.
    # If evader role, invert distance objective.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d = cheb(nx, ny)
        m = mob(nx, ny)
        nobs = near_obst(nx, ny)

        # Dead-end bias: fewer options => worse for pursuer, better for evader.
        dead_pen = 3 if m <= 2 else (1 if m <= 3 else 0)

        if pursuer:
            score = (-d * 5.0) + (m * 0.9) - (nobs * 0.55) - dead_pen * 0.8
            # Additional preference: when distance is similar, prefer the one "more aligned" with opponent.
            vx = 1 if ox > nx else (-1 if ox < nx else 0)
            vy = 1 if oy > ny else (-1 if oy < ny else 0)
            align = (1 if vx != 0 and dx == vx else 0) + (1 if vy != 0 and dy == vy else 0)
            score += align * 0.15
        else:
            score = (d * 5.0) + (m * 0.6) - (nobs * 0.25) + dead_pen * 0.3

        if best_score is None or score > best_score:
            best_score = score
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]