def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    # Predict opponent next step toward its best immediate resource (deterministic heuristic)
    if resources:
        best_r = None
        best_k = None
        for rx, ry in resources:
            k = (man(ox, oy, rx, ry), rx, ry)
            if best_k is None or k < best_k:
                best_k = k
                best_r = (rx, ry)
        trx, try_ = best_r
        dxo = 0 if trx == ox else (1 if trx > ox else -1)
        dyo = 0 if try_ == oy else (1 if try_ > oy else -1)
        pred_ox, pred_oy = ox + dxo, oy + dyo
        if inb(pred_ox, pred_oy) and (pred_ox, pred_oy) in obstacles:
            pred_ox, pred_oy = ox, oy
    else:
        pred_ox, pred_oy = ox, oy

    # Choose a target resource to steal or contest: prioritize where we can beat opponent
    target = None
    best_score = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Higher is better: we want ds-do small/negative; also slightly prefer closer absolute ds
        score = (ds - do, ds, rx, ry)
        if best_score is None or score < best_score:
            best_score = score
            target = (rx, ry)

    # Evaluate candidate moves with local obstacle safety and intercept/steal pressure
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            val = -10**9
        else:
            val = 0
            if target is not None:
                tx, ty = target
                # Reduce distance to contested target; if opponent is likely near, add intercept incentive
                val += -man(nx, ny, tx, ty) * 2.2
                val += -man(nx, ny, pred_ox, pred_oy) * 1.1
                # If we are already closer than opponent to target, increase commitment
                val += 3.0 if man(nx, ny, tx, ty) <= man(ox, oy, tx, ty) else 0.0
            else:
                # No resources: keep pressure near opponent and drift toward center
                cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
                val += -man(nx, ny, pred_ox, pred_oy)
                dx2, dy2 = nx - cx, ny - cy
                val += -(dx2 * dx2 + dy2 * dy2) * 0.01

            # Small tie-breaker: avoid staying if another move is clearly similar
            if dx == 0 and dy == 0:
                val -= 0.05

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move