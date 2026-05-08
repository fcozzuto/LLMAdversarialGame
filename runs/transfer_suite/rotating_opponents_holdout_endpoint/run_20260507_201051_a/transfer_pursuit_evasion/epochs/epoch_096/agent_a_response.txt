def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    pursuer = any(k in role for k in ("purs", "hunt", "chaser", "seeker", "hunter", "pursuer", "catch", "catcher"))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y, tx, ty):
        dx, dy = x - tx, y - ty
        return dx * dx + dy * dy

    def obs_adj_penalty(x, y):
        # Prefer cells with fewer adjacent obstacles (avoid corners/traps)
        cnt = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if not (0 <= nx < w and 0 <= ny < h):
                    cnt += 1
                elif (nx, ny) in obstacles:
                    cnt += 1
        return cnt

    best = (-10**18, 0, 0)
    # deterministic tie-break: order in moves already fixed; keep stable if equal
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        # If adjacent-ish to opponent, discourage staying in capture line for evader
        near = 1 if d <= 4 else 0

        # For pursuer: minimize distance, but avoid obstacle-heavy cells
        # For evader: maximize distance, avoid obstacle traps
        if pursuer:
            score = (-d) - 0.25 * obs_adj_penalty(nx, ny)
            # slight preference to move closer in Chebyshev sense
            score -= 0.05 * (max(abs(nx - ox), abs(ny - oy)))
        else:
            score = (d) - 0.35 * obs_adj_penalty(nx, ny)
            # avoid moves that reduce immediate flee distance too much
            curd = dist2(sx, sy, ox, oy)
            if d < curd:
                score -= 0.2 * (curd - d)
            # if too close, prefer diagonal away (break symmetry deterministically)
            if near:
                away_dx = 0 if nx == ox else (1 if nx > ox else -1)
                away_dy = 0 if ny == oy else (1 if ny > oy else -1)
                if (dx, dy) == (away_dx, away_dy):
                    score += 0.15

        if score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]