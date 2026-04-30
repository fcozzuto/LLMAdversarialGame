def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = {tuple(p) for p in observation["obstacles"]}
    resources = [tuple(p) for p in observation["resources"]]
    if not resources:
        return [0, 0]

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    best_t = None
    best_val = None
    for r in resources:
        dv = dist((sx, sy), r) - 0.9 * dist((ox, oy), r)
        if best_val is None or dv < best_val:
            best_val = dv
            best_t = r

    tx, ty = best_t
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer moving toward our chosen target; tie-break by denying opponent access to same target.
        val = dist((nx, ny), (tx, ty)) - 0.9 * dist((ox, oy), (tx, ty))
        # Secondary: keep away from opponent a bit to reduce contest likelihood.
        val += 0.05 * dist((nx, ny), (ox, oy))
        # Tertiary deterministic tie-break
        val += 0.001 * (dx + 1) + 0.0001 * (dy + 1)
        cand.append((val, dx, dy))
    cand.sort()
    return [int(cand[0][1]), int(cand[0][2])]