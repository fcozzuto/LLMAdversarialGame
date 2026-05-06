def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    # Pick target that favors us: small (our_dist - alpha*opp_dist)
    alpha = 0.75
    best_t = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = int(r[0]), int(r[1])
        od = abs(rx - sx) + abs(ry - sy)
        pd = abs(rx - ox) + abs(ry - oy)
        edge_bias = 0.05 * (min(rx, ry, w - 1 - rx, h - 1 - ry)) * (-1)  # prefer not-too-edge slightly
        key = (od - alpha * pd + edge_bias, rx, ry)
        if best_t is None or key < best_t[0]:
            best_t = (key, rx, ry)
    rx, ry = best_t[1], best_t[2]

    # Choose move that improves reaching the target and reduces opponent progress
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        our_next = abs(rx - nx) + abs(ry - ny)
        opp_next = abs(rx - ox) + abs(ry - oy)  # opponent position unchanged this turn
        # Encourage taking the resource if we step on it
        on_resource = 0 if (nx == rx and ny == ry) else 1
        # Also slightly penalize moving away from any resource
        nearest_any = None
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                tr, ty = int(r[0]), int(r[1])
                d = abs(tr - nx) + abs(ty - ny)
                if nearest_any is None or d < nearest_any:
                    nearest_any = d
        nearest_any = nearest_any if nearest_any is not None else 0
        key = (
            our_next + 0.12 * nearest_any + 0.8 * on_resource - 0.2 * (opp_next - our_next),
            abs(dx) + abs(dy),
            dx,
            dy,
        )
        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]