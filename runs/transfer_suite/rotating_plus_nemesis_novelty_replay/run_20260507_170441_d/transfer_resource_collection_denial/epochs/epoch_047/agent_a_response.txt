def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set((p[0], p[1]) for p in obstacles if p is not None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Target selection: prioritize resources where we are closer than opponent; then tie-break by smaller my distance.
    best_t = None
    best_key = None
    for rx, ry in resources:
        my_d = dist(sx, sy, rx, ry)
        op_d = dist(ox, oy, rx, ry)
        key = (0 if my_d <= op_d else 1, my_d, -(my_d - op_d), rx, ry)
        if best_key is None or key < best_key:
            best_key, best_t = key, (rx, ry)
    tx, ty = best_t

    # Simulate opponent greedy step toward target to estimate contest.
    def opp_greedy_step():
        best = (0, 0)
        best_val = None
        for ddx, ddy in moves:
            nx, ny = ox + ddx, oy + ddy
            if not inb(nx, ny):
                continue
            v = dist(nx, ny, tx, ty)
            # tie-break deterministically to prefer staying still less (more progress)
            key = (v, -(abs(nx - tx) + abs(ny - ty)), ddx, ddy)
            if best_val is None or key < best_val:
                best_val = key
                best = (ddx, ddy)
        return best

    odx, ody = opp_greedy_step()
    nox, noy = ox + odx, oy + ody
    opp_next_d = dist(nox, noy, tx, ty)

    # Move choice: reduce own distance, while preventing opponent advantage; also avoid stepping onto immediate resource if it helps opponent more.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_next_d = dist(nx, ny, tx, ty)
        # If we can reach the target now, strongly prioritize.
        reach = 1 if my_next_d == 0 else 0
        # Estimate whether opponent is closer after its greedy step.
        opp_adv = 1 if opp_next_d < my_next_d else 0
        # Small penalty for moves that move us away.
        away = dist(nx, ny, tx, ty) - dist(sx, sy, tx, ty)
        # Secondary: prefer moves that increase our closeness relative to opponent current.
        rel = dist(ox, oy, tx, ty) - my_next_d
        score = (-(100 * reach), my_next_d, 0 if opp_adv == 0 else 1, away, -rel, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]