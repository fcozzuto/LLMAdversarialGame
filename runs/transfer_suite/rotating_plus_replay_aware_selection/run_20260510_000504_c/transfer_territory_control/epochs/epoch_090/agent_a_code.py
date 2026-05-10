def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = list(map(tuple, observation.get("resources") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    scores = observation.get("scores") or {}
    self_name = observation.get("self_name", "agent_a")
    opponent_name = observation.get("opponent_name", "agent_b")
    my_score = float(scores.get(self_name, 0.0) or 0.0)
    op_score = float(scores.get(opponent_name, 0.0) or 0.0)
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    aggressive = my_score < op_score
    candidates = []
    best = None
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        key = 0
        if resources:
            d = min(dist(nx, ny, rx, ry) for rx, ry in resources)
            key += d * 10
        if (nx, ny) in unclaimed:
            key -= 30
        if aggressive:
            key -= dist(nx, ny, ox, oy) * 0.5
        else:
            key += dist(nx, ny, ox, oy) * 0.5
        candidates.append((key, (dx, dy)))

    if candidates:
        candidates.sort(key=lambda t: (t[0], t[1][0], t[1][1]))
        best = candidates[0][1]
    else:
        best = (0, 0)

    dx, dy = best
    if not (-1 <= dx <= 1 and -1 <= dy <= 1 and isinstance(dx, int) and isinstance(dy, int)):
        return [0, 0]
    return [dx, dy]