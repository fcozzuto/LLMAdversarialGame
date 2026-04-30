def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Target selection: maximize advantage (opponent distance - our distance).
    best_r = None
    best_adv = None
    rc = observation.get("remaining_resource_count", None)
    try:
        rc = int(rc)
    except:
        rc = len(resources)

    for x, y in resources:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        adv = od - sd
        # Slightly favor closer wins when resources are scarce.
        adv2 = adv + (0.05 * (sd == 0)) + (0.01 * (4 - min(sd, 4)) if rc <= 4 else 0.0)
        if best_adv is None or adv2 > best_adv or (adv2 == best_adv and (x, y) < best_r):
            best_adv = adv2
            best_r = (x, y)

    tx, ty = best_r

    # Choose next step to reduce distance to target, avoiding obstacles if possible.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break: lower resulting cheb distance, then prefer moving in x, then y.
    best_move = (0, 0)
    best_d = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Small penalty if we move to/near opponent to reduce being contested.
        opp_d = cheb(nx, ny, ox, oy)
        # Prefer staying away from opponent when disadvantage is large.
        gap = cheb(sx, sy, tx, ty) - cheb(ox, oy, tx, ty)
        penalty = 0
        if gap > 0:
            penalty = -0.02 * max(0, 4 - opp_d)
        score = nd + penalty
        if best_d is None or score < best_d or (score == best_d and (dx, dy) < best_move):
            best_d = score
            best_move = (dx, dy)

    # If all candidate moves were blocked (should be rare), fall back to staying.
    return [int(best_move[0]), int(best_move[1])]