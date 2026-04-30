def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick best target deterministically: prioritize resources where we can arrive earlier than opponent; then minimize our distance; then deterministic tie-break.
    best = None
    best_key = None
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        lead = d_op - d_me  # larger is better
        # If no lead, still choose closest "globally contested" with slight preference toward corners away from us.
        dist_score = d_me
        corner_tie = (rx, ry)
        key = (-lead, dist_score, corner_tie[0], corner_tie[1])
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Evaluate legal moves by greedy improvement to our distance to target; penalize being worse than opponent; avoid obstacles.
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= W or ny < 0 or ny >= H or (nx, ny) in obstacles:
            continue
        d1 = cheb(nx, ny, tx, ty)
        d_me_now = cheb(sx, sy, tx, ty)
        d_op_now = cheb(ox, oy, tx, ty)
        # Prefer moves that reduce our distance; if equal, prefer increasing lead against opponent.
        my_improve = d_me_now - d1
        d_op_after = d_op_now  # opponent unchanged this turn
        lead_after = d_op_after - d1
        # Secondary: slight preference to move generally toward center to avoid getting boxed, deterministically.
        cx, cy = (W - 1) // 2, (H - 1) // 2
        center_pen = cheb(nx, ny, cx, cy)
        key = (-my_improve, -lead_after, d1, center_pen, dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]