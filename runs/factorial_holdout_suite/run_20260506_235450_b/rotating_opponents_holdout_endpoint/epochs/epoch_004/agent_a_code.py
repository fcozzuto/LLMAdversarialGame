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

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        rel = (rx + ry) - (ox + oy)
        far_side = 1 if rel > 0 else 0
        # Prefer resources we can reach sooner and that are "far side" from opponent.
        key = (-(od - sd), sd, -far_side)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    rx, ry = best
    # Choose move that most reduces distance to target; if blocked, consider alternatives.
    moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        d = manh(nx, ny, rx, ry)
        # Small deterministic tie-break: prefer moves that also increase distance from opponent if similar.
        oppd = manh(nx, ny, ox, oy)
        moves.append((d, -oppd, dx, dy))
    if not moves:
        return [0, 0]
    moves.sort()
    return [int(moves[0][2]), int(moves[0][3])]