def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def clamp(v, lo, hi):
        return lo if v < lo else (hi if v > hi else v)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx = clamp(sx + dx, 0, w - 1)
        ny = clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obstacles:
            nx, ny = sx, sy  # avoid stepping into obstacle

        # Evaluate by whether this move makes us closer than the opponent to some remaining resource.
        # Key: minimize (self_dist - opp_dist), then minimize self_dist to that resource,
        # then prefer moves that reduce opponent's closest distance less (keep pressure).
        best_diff = None
        best_selfd = None
        best_oppsd = None
        for rx, ry in resources:
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            diff = sd - od
            if best_diff is None or diff < best_diff or (diff == best_diff and (best_selfd is None or sd < best_selfd)) or (diff == best_diff and sd == best_selfd and od < best_oppsd):
                best_diff = diff
                best_selfd = sd
                best_oppsd = od

        # Prefer more negative diff (we closer), then smaller self distance, then smaller opponent distance to their best target.
        # Also break ties deterministically by preferring direction order from moves list.
        key = (best_diff, best_selfd, best_oppsd, dx, dy)
        if best is None or key < best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]