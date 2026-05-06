def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = [tuple(r) for r in (observation.get("resources") or []) if isinstance(r, (list, tuple)) and len(r) == 2]
    obstacles = set(tuple(o) for o in (observation.get("obstacles") or []) if isinstance(o, (list, tuple)) and len(o) == 2)

    if not resources:
        return [0, 0]

    deltas = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_resource_for_player(px, py):
        return min(resources, key=lambda r: (manh(px, py, r[0], r[1]), r[0], r[1]))

    target = best_resource_for_player(sx, sy)

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d_self = manh(nx, ny, target[0], target[1])
        d_opp = manh(ox, oy, target[0], target[1])
        val = -d_self * 10 + (d_self - d_opp) * 2
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move