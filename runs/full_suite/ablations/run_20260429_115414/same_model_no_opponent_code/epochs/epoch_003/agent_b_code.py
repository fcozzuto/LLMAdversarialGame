def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        resources.append((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def clamp_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return 0, 0
        return dx, dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        # Prefer resources where we are at least as close as opponent; otherwise deny by moving to reduce gap.
        best_r = None
        best_key = None
        for r in resources:
            rx, ry = r
            sd = cheb((sx, sy), (rx, ry))
            od = cheb((ox, oy), (rx, ry))
            # Key: maximize our advantage (negative od+sd), then minimize our distance, then deterministic tie.
            key = (od - sd, sd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_r = r
        tx, ty = best_r

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_d = None
    for dx, dy in moves:
        dx, dy = clamp_move(dx, dy)
        nx, ny = sx + dx, sy + dy
        d_my = cheb((nx, ny), (tx, ty))
        d_opp = cheb((nx, ny), (ox, oy))
        d_res = cheb((ox, oy), (tx, ty))  # opponent's current distance to the same target
        # Score: go to target; discourage giving opponent an easier line by increasing their future proximity; also avoid getting too close.
        score = (d_my * 10) - d_opp
        # If opponent is already closer to target, bias toward moves that reduce our distance most (deterministic gap control).
        if resources:
            sd0 = cheb((sx, sy), (tx, ty))
            if cheb((ox, oy), (tx, ty)) < sd0:
                score = (d_my * 12) - d_opp + (d_res * 0.1)

        # Secondary deterministic tie: prefer move with smaller resulting distance; then prefer lexicographic direction.
        dir_key = (d_my, dx, dy)
        if best is None or score < best or dir_key < best_d:
            best = score
            best_d = dir_key

    # Convert chosen absolute dx,dy already ensured valid by clamp_move
    # Recompute to return exact delta deterministically from best_d.
    # Find the move matching best_d among valid moves.
    target_d, tdx, tdy = best_d
    for dx, dy in moves:
        dx2, dy2 = clamp_move(dx, dy)
        if cheb((sx + dx2, sy + dy2), (tx, ty)) == target_d and dx2 == tdx and dy2 == tdy:
            return [int(dx2), int(dy2)]
    return [0, 0]