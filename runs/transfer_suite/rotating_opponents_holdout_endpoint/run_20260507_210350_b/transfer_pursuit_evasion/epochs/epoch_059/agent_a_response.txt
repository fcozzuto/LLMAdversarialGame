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
    self_is_evader = ("evader" in role_self) or ("runner" in role_self)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best = None
    best_score = None
    # Prefer moving in a direction that changes x/y away/toward opponent; break ties deterministically.
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d = dist2(nx, ny, ox, oy)
        # Obstacle proximity penalty (discourage adjacent moves), deterministic.
        prox = 0
        for ax, ay in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            if (nx + ax, ny + ay) in obstacles:
                prox += 1

        # Corner/edge preference to improve survival vs zigzags: evader stays on edges with line-of-sight blocks.
        edge = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)

        # Role-based objective.
        if self_is_evader:
            # Maximize distance; slight bonus for edge.
            score = d + (1.5 if edge else 0.0) - 2.0 * prox
        else:
            # Minimize distance; slight bonus for moving toward opponent on dominant axis.
            domx = abs(ox - nx) < abs(sx - ox)
            domy = abs(oy - ny) < abs(sy - oy)
            towards_dom = (domx or domy)
            score = -d + (0.6 if towards_dom else 0.0) - 2.0 * prox

        if best_score is None or (score > best_score) or (score == best_score and (dxm, dym) < best):
            best_score = score
            best = (dxm, dym)

    return [best[0], best[1]] if best is not None else [0, 0]