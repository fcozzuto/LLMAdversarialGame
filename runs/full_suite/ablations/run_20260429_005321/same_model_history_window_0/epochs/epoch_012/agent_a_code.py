def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    if not resources:
        return [0, 0]

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) + abs(dy)

    candidates = []
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        score = ds - 0.8 * do
        candidates.append((score, ds, do, rx, ry))
    candidates.sort()
    _, _, _, tx, ty = candidates[0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_for_target():
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            nd = abs(nx - tx) + abs(ny - ty)
            opp_nd = abs((ox + dx) - tx) + abs((oy + dy) - ty)
            # Prefer decreasing distance to target; break ties by anticipating opponent being farther
            val = (nd, -0.15 * opp_nd, abs(dx) + abs(dy))
            if best is None or val < best[0]:
                best = (val, dx, dy)
        if best is None:
            return (0, 0)
        return (best[1], best[2])

    dx, dy = best_for_target()
    return [int(dx), int(dy)]