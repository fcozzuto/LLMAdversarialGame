def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    seen = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst and (x, y) not in seen:
                resources.append((x, y))
                seen.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    self_pos = (sx, sy)
    opp_pos = (ox, oy)

    # If there are resources, head toward the closest that is not blocked, avoiding obstacles.
    if resources:
        target = min(resources, key=lambda r: dist_cheb(self_pos, r))
        best = None
        best_score = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obst:
                continue
            # prefer moving closer to target
            d_to_target = dist_cheb((nx, ny), target)
            d_from_opp = dist_cheb((nx, ny), opp_pos)
            score = -d_to_target * 2 - d_from_opp
            if score > best_score:
                best_score = score
                best = (dx, dy)
        if best is not None:
            return [best[0], best[1]]

    # Fallback: move away from opponent if possible, else toward center
    away_options = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obst:
            continue
        score = dist_cheb((nx, ny), opp_pos)  # farther from opponent
        away_options.append((score, dx, dy))
    if away_options:
        away_options.sort(reverse=True)
        dx = away_options[0][1]
        dy = away_options[0][2]
        return [dx, dy]

    # Last resort: stay
    return [0, 0]