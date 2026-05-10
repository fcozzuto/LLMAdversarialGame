def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def best_step_to(tx, ty):
        best = None
        for dx, dy in dirs:
            nx, ny = ax + dx, ay + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            if (nx, ny) in obs:
                continue
            score = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
            # tie-break toward moving right/down deterministically
            tb = (dx, dy)
            cand = (score, tb)
            if best is None or cand < best[0]:
                best = (cand, (dx, dy))
        if best is None:
            for dx, dy in dirs:
                nx, ny = ax + dx, ay + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                    return [dx, dy]
            return [0, 0]
        return [best[1][0], best[1][1]]

    if res:
        # nearest resource
        tx, ty = min(res, key=lambda p: (p[0] - ax) * (p[0] - ax) + (p[1] - ay) * (p[1] - ay))
        return best_step_to(tx, ty)

    # fallback: chase opponent deterministically
    tx = clamp(ox, 0, w - 1)
    ty = clamp(oy, 0, h - 1)
    return best_step_to(tx, ty)