def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def manhattan(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    # Heuristic: go for nearest resource while discouraging moves that stay on the opponent's row/col.
    best_move = None
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if resources:
            nd = None
            for rx, ry in resources:
                d = manhattan(nx, ny, rx, ry)
                if nd is None or d < nd:
                    nd = d
        else:
            nd = 0
        od = manhattan(nx, ny, ox, oy)

        penalty = 0
        if ny == oy:
            penalty += 6  # avoid staying on opponent's sweep row
        if nx == ox:
            penalty += 2  # slight avoidance of sweep column
        # encourage changing row when opponent is close in row-wise sense
        if abs(ny - oy) < abs(sy - oy):
            penalty -= 1
        if abs(nx - ox) < abs(sx - ox):
            penalty -= 0  # neutral, deterministic

        score = nd * 9 + od + penalty
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]