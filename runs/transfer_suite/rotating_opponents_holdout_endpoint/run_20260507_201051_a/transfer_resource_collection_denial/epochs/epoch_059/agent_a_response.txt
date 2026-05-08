def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def best_dir(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):  # fallback to stay
            return [0, 0]
        if (nx, ny) in obstacles:
            # try axis-aligned alternative deterministically
            opts = [(dx, 0), (0, dy), (0, 0)]
            for adx, ady in opts:
                nx2, ny2 = sx + adx, sy + ady
                if 0 <= nx2 < w and 0 <= ny2 < h and (nx2, ny2) not in obstacles:
                    return [adx, ady]
            return [0, 0]
        return [dx, dy]

    if resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best_key = None
        best_t = None
        # maximize opponent advantage over us (opp farther? actually we want ours closer => opp_dist - self_dist large)
        for x, y in sorted(resources):
            ds = cheb(sx, sy, x, y)
            do = cheb(ox, oy, x, y)
            adv = do - ds
            # prefer nearer resources, and nearer center to reduce wandering; then lexicographic
            key = (adv, -ds, -abs(x - cx) - abs(y - cy), -x, -y)
            if best_key is None or key > best_key:
                best_key, best_t = key, (x, y)
        return best_dir(best_t[0], best_t[1])

    # No visible resources: head toward center, avoiding obstacles
    targetx, targety = int(round((w - 1) / 2.0)), int(round((h - 1) / 2.0))
    return best_dir(targetx, targety)