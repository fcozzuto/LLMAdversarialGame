def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
    resset = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resset.add((p[0], p[1]))

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx + dy

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx0, dy0 in deltas:
        nx, ny = x + dx0, y + dy0
        if inb(nx, ny):
            moves.append((dx0, dy0, nx, ny))
    if not moves:
        return [0, 0]

    center = (w // 2, h // 2)
    best_res = None
    if resset:
        best_res = min(resset, key=lambda r: dist((x, y), r))

    best = None
    for dx0, dy0, nx, ny in moves:
        here = (nx, ny)
        score = 0

        if here in resset:
            score += 100000
            score -= dist(here, (ox, oy)) * 2

        if best_res is not None:
            score -= dist(here, best_res) * 10
        else:
            score -= dist(here, center) * 2

        oppd = dist(here, (ox, oy))
        score += oppd * 1.5

        # Avoid moving into an obstacle-adjacent trap: discourage stepping next to obstacles
        if obs:
            adj_obs = 0
            for ddx in (-1, 0, 1):
                for ddy in (-1, 0, 1):
                    if ddx == 0 and ddy == 0:
                        continue
                    if (nx + ddx, ny + ddy) in obs:
                        adj_obs += 1
            score -= adj_obs * 0.3

        if best is None or score > best[0] or (score == best[0] and (dx0, dy0) < best[1]):
            best = (score, (dx0, dy0))

    return [best[1][0], best[1][1]]