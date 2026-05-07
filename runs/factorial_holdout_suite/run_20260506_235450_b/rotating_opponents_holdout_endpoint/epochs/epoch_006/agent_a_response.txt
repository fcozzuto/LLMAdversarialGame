def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [int(dx), int(dy)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            nx, ny = sx, sy

        move_score = None
        # Evaluate best resource under this next position.
        for rx, ry in resources:
            if (rx, ry) in obs_set:
                continue
            d_self = dist(nx, ny, rx, ry)
            d_opp = dist(ox, oy, rx, ry)
            # Prefer resources we can reach earlier; otherwise still prefer closer ones.
            # Larger score is better.
            score = (d_opp - d_self) * 10 - d_self
            if move_score is None or score > move_score:
                move_score = score

        # Deterministic tie-break: first in deltas order.
        if best is None or move_score > best:
            best = move_score
            best_move = [int(nx - sx), int(ny - sy)]

    return best_move