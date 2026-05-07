def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set((p[0], p[1]) for p in obstacles)
    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # If opponent is closer to some resource, deny by moving to its "arrival front" (intercept cell).
    best_target = None
    best_adv = -10**9
    for rx, ry in resources:
        my_d = man(sx, sy, rx, ry)
        op_d = man(ox, oy, rx, ry)
        adv = (op_d - my_d)  # positive means we are closer (or less behind)
        # Prefer resources where we are not far behind; break ties by closeness
        key = (adv, -my_d, -rx, -ry)
        if best_target is None or key > best_key:
            best_key, best_target = key, (rx, ry)
    tx, ty = best_target

    # Intercept: aim for the cell on a shortest path from opponent to target.
    # Move one step from our position toward the chosen intercept direction.
    # Choose intercept among up to 4 neighbors of opponent that reduce their distance to target the most.
    best_ix, best_iy = tx, ty
    best_ipd = man(ox, oy, tx, ty)
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = ox + dx, oy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        d = man(nx, ny, tx, ty)
        if d < best_ipd:
            best_ipd = d
            best_ix, best_iy = nx, ny

    # Score candidate moves: (1) progress to intercept, (2) progress to target, (3) avoid stepping near opponent.
    # Deterministic tie-breaking via lexicographic of dx,dy order.
    opp_dist_now = man(sx, sy, ox, oy)
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_int = man(nx, ny, best_ix, best_iy)
        d_t = man(nx, ny, tx, ty)
        d_op = man(nx, ny, ox, oy)

        # Main objective: minimize distance to intercept, then target.
        progress_int = -d_int
        progress_t = -d_t

        # Deny: if opponent is approaching, reduce their advantage by getting closer to target.
        my_d = man(nx, ny, tx, ty)
        op_d_next = man(ox, oy, tx, ty)
        deny = (op_d_next - my_d)

        # Safety: don't allow opponent to be too close; small penalty for moving adjacent.
        safety = -1 if d_op <= 1 else 0

        score = (progress_int * 10_000) + (progress_t * 100) + deny * 10 + safety
        if score > best_score or (score == best_score and (dx, dy) > (best_move[0] - sx, best_move[1] - sy)):
            best_score = score
            best_move = [nx - sx, ny - sy]

    return [int(best_move[0]), int(best_move[1])]