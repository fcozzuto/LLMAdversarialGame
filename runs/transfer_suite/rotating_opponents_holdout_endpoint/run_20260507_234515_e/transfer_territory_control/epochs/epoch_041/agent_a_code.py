def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        cells = observation.get(key) or []
        for p in cells:
            if p is None:
                continue
            if isinstance(p, dict):
                x = p.get("x", p.get(0))
                y = p.get("y", p.get(1))
            elif isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
            else:
                continue
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                out.add((x, y))
        return out

    obstacles = to_set("obstacles") | to_set("resource_obstacles")
    unclaimed = to_set("unclaimed_cells") | to_set("unclaimed") | to_set("neutral_cells")
    opp_terr = to_set("opponent_territory")
    resources = to_set("resources") | to_set("resource_cells") | to_set("resource_locations")

    targets = unclaimed if unclaimed else (opp_terr if opp_terr else resources)
    if not targets:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles and (dx, dy) != (0, 0):
            continue
        d_to_t = min(dist2((nx, ny), t) for t in targets)
        d_to_o = dist2((nx, ny), (ox, oy))
        score = -d_to_t + 0.05 * d_to_o
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best
    return [0, 0]