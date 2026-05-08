def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    tleft = observation.get("turns_remaining", 0)

    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs_set.add((p[0], p[1]))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def score_target(nx, ny, tx, ty):
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # If opponent can reach much earlier, penalize heavily.
        # Prefer targets we can reach at least as fast as opponent.
        return (ds - do * 0.95) + (0 if ds <= do else 5.0) + ds * 0.02

    # If we are near resources or very late, just take the closest safe move.
    if not resources or tleft <= 2:
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            if not resources:
                return [dx, dy]  # deterministic fallback
            key = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    best_overall = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Evaluate move by best target we can secure over opponent.
        # Also avoid stepping into obstacle-adjacent traps by using a small penalty for being "near" obstacles.
        near_obs = 0
        for ax, ay in ((nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1), (nx-1, ny-1), (nx+1, ny-1), (nx-1, ny+1), (nx+1, ny+1)):
            if (ax, ay) in obs_set:
                near_obs += 1
        best_target = None
        for rx, ry in resources:
            key = score_target(nx, ny, rx, ry)
            if best_target is None or key < best_target:
                best_target = key
        # Small deterministic tie-break using direction preference toward board center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = cheb(nx, ny, cx, cy) * 0.001
        total = best_target + near_obs * 0.03 + center_bias
        if best_overall is None or total < best_overall[0] or (total == best_overall[0] and (dx, dy) < (best_overall[1], best_overall[2])):
            best_overall = (total, dx, dy)

    return [best_overall[1], best_overall[2]]