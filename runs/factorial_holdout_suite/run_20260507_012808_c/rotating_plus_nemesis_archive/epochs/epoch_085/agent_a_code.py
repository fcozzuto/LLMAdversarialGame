def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = observation.get("obstacles") or []
    obstacles = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = observation.get("resources") or []
    resources = []
    for r in res:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx + dy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        if resources:
            d_self = min(dist((nx, ny), rp) for rp in resources)
            d_opp = min(dist((ox, oy), rp) for rp in resources)
            score = (d_opp - d_self) * 1000 - dist((nx, ny), (ox, oy)) * 2
        else:
            score = dist((nx, ny), (ox, oy)) * 10

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best