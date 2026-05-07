def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                if (x, y) not in obstacles:
                    resources.append((x, y))

    if not resources or (sx, sy) in resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Target: maximize (opp_dist - our_dist); tie-break: smaller our_dist; then lexicographic.
    best = None
    best_key = None
    for rx, ry in resources:
        d_ours = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        adv = d_opp - d_ours
        key = (-(adv), d_ours, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # If blocked right at target direction, keep moving (still deterministic) by evaluating candidate moves.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def clamp_dir(d):
        if d < 0: return -1
        if d > 0: return 1
        return 0

    preferred = (clamp_dir(tx - sx), clamp_dir(ty - sy))
    ordered = []
    for dx, dy in moves:
        if (dx, dy) == preferred:
            ordered.insert(0, (dx, dy))
        else:
            ordered.append((dx, dy))

    best_move = (0, 0)
    best_move_key = None
    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_ours = cheb(nx, ny, tx, ty)
        # Greedy improvement plus avoid giving opponent a faster route to the same cell.
        d_opp = cheb(ox, oy, tx, ty)
        key = (d_ours, (d_opp - d_ours) * -1, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]