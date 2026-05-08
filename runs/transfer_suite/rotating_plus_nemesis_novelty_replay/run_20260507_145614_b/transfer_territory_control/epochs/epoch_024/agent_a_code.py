def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))

    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if p and len(p) == 2:
            obstacles.add((p[0], p[1]))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if p and len(p) == 2:
            res.append((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Deterministic target: nearest resource if any, else move toward opponent
    if res:
        tx, ty = min(res, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    else:
        tx, ty = ox, oy

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer closeness to target; small penalty for staying; tie-break deterministically
        d_to_t = abs(nx - tx) + abs(ny - ty)
        d_to_o = abs(nx - ox) + abs(ny - oy)
        score = (-(d_to_t), d_to_o, abs(dx) + abs(dy), nx, ny)
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best
    # Fallback: deterministic safe move if any
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
    return [0, 0]