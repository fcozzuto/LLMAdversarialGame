def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))
    if not res:
        return [0, 0]

    def dist_cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx >= dy else dy

    # Select target we can reach earlier than opponent; break ties by lower opponent distance then by fixed ordering.
    best = None
    best_key = None
    for tx, ty in res:
        self_d = dist_cheb((sx, sy), (tx, ty))
        opp_d = dist_cheb((ox, oy), (tx, ty))
        # Larger score is better
        score = opp_d - self_d
        # Prefer strictly winning; if equal, prefer closer to us (fewer turns), then farther from opponent (harder to steal), then deterministic order.
        key = (score, -(self_d), -(opp_d), -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    # Candidate moves: prefer diagonal/straight directions that reduce distance to target; deterministic tie-break order.
    moves = [
        (0, 0), (1, 0), (0, 1), (-1, 0), (0, -1),
        (1, 1), (1, -1), (-1, 1), (-1, -1)
    ]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d0 = dist_cheb((sx, sy), (tx, ty))
        d1 = dist_cheb((nx, ny), (tx, ty))
        # Primary: progress toward target. Secondary: prevent opponent from gaining more next-step.
        # Predict opponent next-step greedily toward same target.
        best_opp = dist_cheb((ox, oy), (tx, ty))
        for odx, ody in moves:
            onx, ony = ox + odx, oy + ody
            if 0 <= onx < w and 0 <= ony < h and (onx, ony) not in obst:
                dd = dist_cheb((onx, ony), (tx, ty))
                if dd < best_opp:
                    best_opp = dd
        # Move key: maximize improvement, then maximize advantage (opp_next - self_next), then deterministic order.
        opp_adv = best_opp - d1
        key = (d0 - d1, opp_adv, -abs(nx - tx) - abs(ny - ty), -dx, -dy)
        if best_mkey is None or key > best_mkey:
            best_mkey = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]