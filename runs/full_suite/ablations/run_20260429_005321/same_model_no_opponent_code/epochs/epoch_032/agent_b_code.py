def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = int(x) + dx, int(y) + dy
        if inside(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Pick a resource we can contest: minimize (opp_dist - my_dist), i.e., maximize my advantage.
    best = None
    best_adv = None
    for rx, ry in resources:
        d_my = cheb(int(x), int(y), rx, ry)
        d_opp = cheb(int(ox), int(oy), rx, ry)
        adv = d_opp - d_my  # larger is better
        # Tie-break: prefer closer overall to reduce time-to-score
        key = (adv, -min(d_my, d_opp))
        if best is None or key > best:
            best = key
            best_r = (rx, ry)

    if not resources:
        # No resources visible: move to maximize distance from opponent while staying safe
        best_move = None
        best_score = None
        for dx, dy, nx, ny in legal:
            d = cheb(nx, ny, int(ox), int(oy))
            s = (d, -abs(nx - int(w / 2)) - abs(ny - int(h / 2)))
            if best_score is None or s > best_score:
                best_score = s
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    tx, ty = best_r
    cur_d = cheb(int(x), int(y), tx, ty)

    # Choose move that reduces distance to target; if equal, prefer increasing distance from opponent.
    chosen = None
    chosen_key = None
    for dx, dy, nx, ny in legal:
        d_to_t = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, int(ox), int(oy))
        # Strongly prefer stepping onto the target when possible
        on_target = 1 if (nx, ny) == (tx, ty) else 0
        # Also nudge toward the target even if it doesn't strictly reduce (diagonal control).
        dist_gain = cur_d - d_to_t
        key = (on_target, dist_gain, d_opp, -cheb(nx, ny, tx, ty), -abs(nx - tx) - abs(ny - ty), dx, dy)
        if chosen_key is None or key > chosen_key:
            chosen_key = key
            chosen = (dx, dy)
    return [int(chosen[0]), int(chosen[1])]