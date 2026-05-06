def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        # Evaluate the move by how strongly it can claim a resource vs opponent.
        # Primary: maximize (opp_d - self_d_next) so we "arrive first".
        # Secondary: minimize self distance to reduce lag.
        # Tertiary: deterministic tie by coordinates.
        local_best = None
        local_best_key = None
        for cx, cy in resources:
            self_dn = cheb(nx, ny, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            key = (opp_d - self_dn, -self_dn, -cx, -cy)
            if local_best_key is None or key > local_best_key:
                local_best_key = key
                local_best = (cx, cy)
        if local_best_key is None:
            continue

        # Small diversification: prefer moves that also don't worsen "threat" too much.
        # Use best resource score as move value; add penalty if we move away from the best target.
        bx, by = local_best
        base_self_dn = cheb(nx, ny, bx, by)
        base_self_d = cheb(sx, sy, bx, by)
        penalty = base_self_dn - base_self_d  # prefer improvement (smaller)
        move_key = (local_best_key[0], -local_best_key[1], penalty, dx, dy)
        if best_key is None or move_key < best_key:
            best_key = move_key
            best_move = (dx, dy)

    # If all moves filtered out (e.g., surrounded by obstacles), allow staying.
    if best_key is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]