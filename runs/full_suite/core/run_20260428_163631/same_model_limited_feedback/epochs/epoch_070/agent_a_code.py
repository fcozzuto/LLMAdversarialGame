def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]
    gw, gh = observation["grid_width"], observation["grid_height"]

    obs = set((p[0], p[1]) for p in obstacles)
    res = [(p[0], p[1]) for p in resources]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < gw and 0 <= ny < gh

    def d(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not res:
        # No visible resources: drift toward opponent's side cautiously
        targets = [(gw // 2, gh // 2), (gw - 1, gh - 1), (0, 0)]
        best = None
        for tx, ty in targets:
            score = d(x, y, tx, ty) - 0.2 * d(ox, oy, tx, ty)
            if best is None or score < best[0]:
                best = (score, tx, ty)
        tx, ty = best[1], best[2]
    else:
        # Pick resource that we can reach with advantage over opponent
        tx = ty = res[0][0], res[0][1]
        best_val = None
        for rx, ry in res:
            sd = d(x, y, rx, ry)
            od = d(ox, oy, rx, ry)
            val = (od - sd) * 2 - sd * 0.3
            # mild preference for closer to our diagonal toward their corner when tied
            val += -0.05 * ((rx - (gw - 1)) ** 2 + (ry - (gh - 1)) ** 2)
            if best_val is None or val > best_val:
                best_val = val
                tx, ty = rx, ry

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        sd = d(nx, ny, tx, ty)
        od = d(nx, ny, ox, oy)
        # Encourage approaching target, discourage moving into opponent vicinity
        step_score = sd * 1.0 - (od * 0.15)
        # Prefer staying if no clear improvement
        step_score += 0.02 * (1 if (dx == 0 and dy == 0) else 0)
        if best_score is None or step_score < best_score:
            best_score = step_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]