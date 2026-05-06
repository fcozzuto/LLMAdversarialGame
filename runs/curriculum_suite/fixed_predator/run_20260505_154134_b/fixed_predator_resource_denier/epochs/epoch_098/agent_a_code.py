def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cand = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy, nx, ny in legal:
            d = abs(nx - tx)
            dy2 = abs(ny - ty)
            dd = d if d > dy2 else dy2
            key = (dd, nx + ny)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    best_move = None
    best_score = None
    for dx, dy, nx, ny in legal:
        self_to = [cheb(nx, ny, rx, ry) for rx, ry in resources]
        opp_to = [cheb(ox, oy, rx, ry) for rx, ry in resources]

        # Pick the resource we'd get to "best" relative to opponent after this move.
        best_cell_score = None
        best_tiebreak = None
        for i, (rx, ry) in enumerate(resources):
            sd = self_to[i]
            od = opp_to[i]
            # Prefer resources where we arrive earlier or contest closely, with tie-break by smaller self distance.
            score = (od - sd, -(sd), -(rx + ry))
            if best_cell_score is None or score > best_cell_score:
                best_cell_score = score
                best_tiebreak = (sd, rx, ry)

        # Also encourage shortening distance to nearest resource overall to keep momentum.
        nearest_self = min(self_to)
        nearest_opp = min(opp_to)
        global_score = (best_cell_score[0], best_cell_score[1], -nearest_self, nearest_opp)
        tiebreak = (best_tiebreak[0], best_tiebreak[1], best_tiebreak[2], nx + ny)

        if best_score is None or global_score > best_score or (global_score == best_score and tiebreak < best_move[0]):
            best_score = global_score
            best_move = (tiebreak, dx, dy)

    return [int(best_move[1]), int(best_move[2])]