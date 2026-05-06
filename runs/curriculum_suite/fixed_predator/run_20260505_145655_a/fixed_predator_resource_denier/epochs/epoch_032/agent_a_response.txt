def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            t = (int(r[0]), int(r[1]))
            if t not in obstacles:
                resources.append(t)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    def score_cell(cx, cy, ax, ay):
        # Advantage: positive means our closeness beats opponent on this cell.
        best = -10**18
        for rx, ry in resources:
            selfd = abs(cx - rx) + abs(cy - ry)
            oppd = abs(ox - rx) + abs(oy - ry)
            best = max(best, (oppd - selfd) * 6 - selfd)
        return best

    def opp_greedy_next():
        best_sc = -10**18
        best = (ox, oy)
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            # Opponent tries to maximize its own advantage (towards resources).
            sc = -score_cell(nx, ny, sx, sy) - (abs(nx - sx) + abs(ny - sy)) * 0.1
            if sc > best_sc:
                best_sc = sc
                best = (nx, ny)
        return best

    px, py = opp_greedy_next()

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        val = score_cell(nx, ny, sx, sy)
        # Intercept: move to reduce distance to predicted opponent next.
        val += -(abs(nx - px) + abs(ny - py)) * 0.8
        # Small tie-breaker toward resources actually present at/near the move.
        for rx, ry in resources:
            if abs(nx - rx) + abs(ny - ry) == 0:
                val += 1000
                break
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]