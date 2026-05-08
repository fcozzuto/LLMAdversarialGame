def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role_self = str(observation.get("self_role", "") or "").lower()
    is_pursuer = any(k in role_self for k in ("pursuer", "chaser", "hunter"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    def obstacle_prox(nx, ny):
        # Small deterministic penalty when near obstacles (encourages smoother paths)
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    pen += 1
        return pen

    best_dxdy = (0, 0)
    best_score = None

    # Deterministic tie-break order: as listed in moves
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue

        d_now = cheb(nx, ny, ox, oy)

        # One-step lookahead against immediate obstacle trapping: pick moves that
        # improve our objective even if opponent gets a favorable step next turn.
        opp_best_for_them = 10**9
        for odx, ody in moves:
            tx, ty = ox + odx, oy + ody
            if not inb(tx, ty) or (tx, ty) in obstacles:
                continue
            opp_best_for_them = min(opp_best_for_them, cheb(nx, ny, tx, ty))

        prox = obstacle_prox(nx, ny)

        if is_pursuer:
            # Pursuer: minimize distance to opponent; also prefer states that keep distance small
            score = d_now * 10 + opp_best_for_them * 2 + prox
        else:
            # Evader: maximize distance; also avoid allowing opponent to get instantly closer
            score = (-d_now) * 10 + (-opp_best_for_them) * 3 - prox

        if best_score is None or score < best_score:
            best_score = score
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]