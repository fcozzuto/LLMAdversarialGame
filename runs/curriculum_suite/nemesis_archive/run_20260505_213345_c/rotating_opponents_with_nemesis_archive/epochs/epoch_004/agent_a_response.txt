def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    if any(sx == r[0] and sy == r[1] for r in resources):
        return [0, 0]

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx*dx + dy*dy

    if not resources:
        # No resources: move toward center-ish deterministically while avoiding obstacles
        tx, ty = w // 2, h // 2
        best = None
        bestv = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                v = dist2(nx, ny, tx, ty)
                if bestv is None or v < bestv or (v == bestv and (dx, dy) < best):
                    bestv = v
                    best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Evaluate each candidate by "advantage" = my_dist - opp_dist (lower is better for us).
    # If we can reach a resource where we are at least as close as opponent, prefer that; otherwise minimize advantage then my distance.
    best = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Deterministic multi-resource objective: pick the resource we care about most from this position.
        # Key is best achievable advantage; then tie-break by our distance and move preference.
        best_adv = None
        best_my_d = None
        for rx, ry in resources:
            myd = dist2(nx, ny, rx, ry)
            opd = dist2(ox, oy, rx, ry)
            adv = myd - opd
            # Prefer more negative advantage; if equal, prefer smaller my distance.
            if best_adv is None or adv < best_adv or (adv == best_adv and myd < best_my_d):
                best_adv = adv
                best_my_d = myd

        favorable = 0 if best_adv <= 0 else 1  # 0 means "we are no farther than opponent" on some resource.
        key = (favorable, best_adv, best_my_d, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]