def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    self_path = observation.get("self_path") or []
    opp_path = observation.get("opponent_path") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    best_score = -10**18

    prev = self_path[-1] if self_path else None
    opp_prev = opp_path[-1] if opp_path else None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d_op = dist(nx, ny, ox, oy)
        score = -d_op

        if (nx, ny) in unclaimed:
            score += 50

        if prev is not None and (nx, ny) == tuple(prev):
            score -= 1

        if opp_prev is not None and (nx, ny) == tuple(opp_prev):
            score += 1

        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]