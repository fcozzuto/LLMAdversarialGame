def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs if p is not None and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not inb(sx, sy) or w <= 0 or h <= 0:
        return [0, 0]

    # Choose a target resource deterministically
    tx, ty = None, None
    if resources:
        best_key = None
        for rx, ry in resources:
            ds = abs(sx - rx) + abs(sy - ry)
            do = abs(ox - rx) + abs(oy - ry)
            # Prefer we arrive earlier and that opponent is relatively far
            key = (do - ds, -ds, -(rx * 9 + ry), rx, ry)
            # Larger (do-ds) first; then smaller ds -> larger -ds; deterministic tie-breakers
            if best_key is None or key > best_key:
                best_key = key
                tx, ty = rx, ry
    else:
        # No resources: drift to center-ish while staying safe
        tx, ty = w // 2, h // 2

    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Value: move closer to target, increase distance from opponent, and if resources exist
        # also reduce opponent's closeness to the same target.
        if tx is not None:
            d_self = man(nx, ny, tx, ty)
            d_opp_to_target = man(ox, oy, tx, ty)
            d_opp_move = man(ox + (1 if ox < tx else -1 if ox > tx else 0), oy + (1 if oy < ty else -1 if oy > ty else 0), tx, ty)
            # We don't know opponent move, but penalize states where target is very close to opponent.
            opp_term = d_opp_to_target - d_opp_move
            val = -d_self + 0.25 * (man(nx, ny, ox, oy)) + 0.1 * opp_term
            # If standing still, slightly penalize to keep progress
            if dx == 0 and dy == 0:
                val -= 0.05
        else:
            val = 0.3 * man(nx, ny, ox, oy) - man(nx, ny, w // 2, h // 2)
        # Resource presence: also consider immediate pickup potential
        if resources:
            for rx, ry in resources:
                if nx == rx and ny == ry:
                    val += 1e6
                    break

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]