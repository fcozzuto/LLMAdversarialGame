def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    r0 = min(resources, key=lambda r: cheb(ox, oy, r[0], r[1]))
    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs:
            continue
        val = cheb(ox, oy, r0[0], r0[1]) - cheb(nx, ny, r0[0], r0[1])
        if observation.get("scores") is not None and isinstance(observation["scores"], (list, tuple)) and len(observation["scores"]) >= 2:
            val += 0.1 * (observation["scores"][0] - observation["scores"][1])
        dists = []
        for i, r in enumerate(resources):
            dists.append((cheb(nx, ny, r[0], r[1]) - cheb(ox, oy, r[0], r[1]), i))
            if len(dists) > 6:
                break
        for t, _ in sorted(dists)[:3]:
            val += 0.5 * (-t)
        if best is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]