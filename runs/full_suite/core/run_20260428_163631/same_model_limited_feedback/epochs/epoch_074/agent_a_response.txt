def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_name = observation.get("self_name", "")
    opponent_name = observation.get("opponent_name", "")

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_resources = [tuple(r) for r in resources if tuple(r) not in obstacles]

    if not cur_resources:
        # fallback: move to maximize distance from opponent while avoiding obstacles
        best = (None, -1e18)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            u = dist((nx, ny), (ox, oy))
            # deterministic tie-breaker: prefer lower dx, then lower dy
            if u > best[1] or (u == best[1] and (dx, dy) < best[0]):
                best = ((dx, dy), u)
        if best[0] is None:
            return [0, 0]
        return [best[0][0], best[0][1]]

    # Choose a target resource where we have positional advantage over the opponent
    def res_key(r):
        # stable deterministic ordering by coordinates
        return (r[0], r[1])

    best_res = None
    best_adv = -1e18
    for r in sorted(cur_resources, key=res_key):
        ds = dist((sx, sy), r)
        do = dist((ox, oy), r)
        adv = (do - ds)  # positive means we're closer
        # also prefer nearer resources to reduce travel time
        score = adv * 10.0 - ds
        if score > best_adv:
            best_adv = score
            best_res = r

    tx, ty = best_res
    best_move = (0, 0)
    best_u = -1e18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        d_target = dist((nx, ny), (tx, ty))
        d_opp = dist((nx, ny), (ox, oy))

        # Heuristic: rush best target, keep away a bit from opponent, avoid letting opponent close too fast
        # Also discourage "drifting" away from our current advantage.
        d_self_now = dist((sx, sy), (tx, ty))
        adv_now = dist((ox, oy), (tx, ty)) - d_self_now
        adv_next = dist((ox, oy), (tx, ty)) - d_target

        u = (adv_next - adv_now) * 5.0 + (-d_target) + d_opp * 0.15

        # Deterministic tie-breaker
        if u > best_u or (u == best_u and (dx, dy) < best_move):
            best_u = u
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]